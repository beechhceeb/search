// static/js/index.js


async function init() {
  // --- Get references to elements ---
  const form = document.getElementById("imageForm");
  const imageInput = document.getElementById("imageInput");
  const resultsContainer = document.getElementById("results-container");
  const progressContainer = document.getElementById("progressContainer"); // For file reading progress
  const mainContent = document.getElementById("main-content"); // The div containing the form

  // --- Initialize the FILE READING progress bar ---
  const fileProgressBar = new ProgressBar.Line("#progressContainer", {
    strokeWidth: 4,
    easing: "easeInOut",
    duration: 200,
    color: "#FFEA82",
    trailColor: "#eee",
    trailWidth: 1,
    svgStyle: { width: "100%", height: "100%" },
    from: { color: "#FFEA82" },
    to: { color: "#ED6A5A" },
    step: (state, bar) => {
      bar.path.setAttribute("stroke", state.color);
    },
  });

  if (!form) {
    return;
  }
  let requiredFields = [];
  try {
    const resp = await fetch("/exif-whitelist");
    if (resp.ok) {
      requiredFields = await resp.json();
    } else {
      console.error("Failed to fetch EXIF whitelist");
    }
  } catch (e) {
    console.error("Error fetching EXIF whitelist", e);
  }

  // --- Form Submission Handler ---
  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    const files = imageInput.files;
    if (!files.length) {
      alert("Please select one or more JPG/JPEG image files.");
      return;
    }

    // --- Prepare for processing ---
    const exifDataArray = [];

    const loadingMessages = [
      "Checking your images…",
      "Extracting your gear data…",
      "Scanning focal lengths…",
      "Looking for hidden lens gems…",
      "Detecting your signature shooting style…",
      "Comparing you to the pros (favourably)…",
    ];

    let processedFiles = 0;
    let filesToProcess = 0;

    // Filter for JPEG and count valid files
    const validFiles = Array.from(files).filter((file) => {
      if (file.type.match("image/jpeg") || file.type.match("image/jpg")) {
        return true;
      } else {
        console.warn(`Skipping non-JPEG file: ${file.name}`);
        return false;
      }
    });

    filesToProcess = validFiles.length;

    if (filesToProcess === 0) {
      alert("No valid JPG/JPEG files selected.");
      return; // Stop if no valid files
    }

    // --- Reset UI ---
    mainContent.style.display = "none"; // Hide the form section
    progressContainer.style.display = "block"; // Ensure progress bar container is visible
    fileProgressBar.set(0); // Reset file reading progress bar
    resultsContainer.innerHTML =
      '<p class="text-center mt-20vh">Extracting exif from image data...</p>'; // Initial status message

    // --- Process Valid Files ---
    validFiles.forEach((file) => {
      const reader = new FileReader();

      reader.onload = function (e) {
        const arrayBuffer = e.target.result;
        const binaryString = convertArrayBufferToBinaryString(arrayBuffer);

        let exifData;
        let filteredExifData = {}; // Include filename

        try {
          exifData = piexif.load(binaryString);
          const filteredExifData = {};
          requiredFields.forEach((field) => {
            if (exifData["0th"] && exifData["0th"][piexif.ImageIFD[field]]) {
              filteredExifData[field] = exifData["0th"][piexif.ImageIFD[field]];
            } else if (
              exifData["Exif"] &&
              exifData["Exif"][piexif.ExifIFD[field]]
            ) {
              filteredExifData[field] = exifData["Exif"][piexif.ExifIFD[field]];
            } else if (
              exifData["Interop"] &&
              exifData["Interop"][piexif.InteropIFD[field]]
            ) {
              filteredExifData[field] =
                exifData["Interop"][piexif.InteropIFD[field]];
            }
          });
          exifDataArray.push(filteredExifData);
        } catch (error) {
          console.warn(`Could not read EXIF for ${file.name}: ${error}`);
          filteredExifData.error = `Could not read EXIF: ${error}`;
        } finally {
          exifDataArray.push(filteredExifData); // Add data (even if empty/error)
          processedFiles++;
          // Update file reading progress bar
          fileProgressBar.animate(processedFiles / filesToProcess); // Animate progress
          let messageIndex; // Default message index
          if (processedFiles >= loadingMessages.length * 80) {
            messageIndex = loadingMessages.length - 1; // Last message
          } else {
            messageIndex =
              Math.floor(processedFiles / 80) % loadingMessages.length;
          }
          const loadingMessage = loadingMessages[messageIndex];
          resultsContainer.innerHTML = `<div class="text-center mt-20vh"><p>${processedFiles}/${filesToProcess}</p><p> ${loadingMessage}</p></div>`;

          // Check if all valid files are processed
          if (processedFiles === filesToProcess) {
            resultsContainer.innerHTML =
              '<p class="text-center mt-20vh">Sending data for analysis...</p>'; // Update status
            sendExifDataToServer(exifDataArray); // Send data
          }
        }
      };

      reader.onerror = function (e) {
        console.error(`Error reading file ${file.name}:`, e);
        // Still count as processed to avoid getting stuck
        processedFiles++;
        exifDataArray.push({ filename: file.name, error: "File read error" }); // Add error placeholder
        fileProgressBar.animate(processedFiles / filesToProcess); // Update progress

        if (processedFiles === filesToProcess) {
          resultsContainer.innerHTML =
            '<p class="text-center mt-20px">Sending data for analysis (with some errors)...</p>';
          sendExifDataToServer(exifDataArray);
        }
      };

      reader.readAsArrayBuffer(file); // Read as ArrayBuffer
    });
  }); // End form submit listener

  // --- Function to Send Data and Handle Response ---
  function sendExifDataToServer(exifDataArray) {

    fetch("/process-exif", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ exifData: exifDataArray }), // Send the extracted data
    })
      .then((response) => {
        // Hide the file reading progress bar container once fetch starts responding
        progressContainer.style.display = "none";

        if (response.ok) {
          return response.json(); // Expect HTML fragment as text
        } else {
          // Try to get error text from response body for better debugging
          return response.text().then((text) => {
            throw new Error(
              'Analysis failed. Server responded with status ${response.status}. ${text || "(No further details)"}',
            );
          });
        }
      })
      .then((data) => {
        // --- SUCCESS ---
        // Hide the header banner
        document.getElementById("header-banner").style.display = "none";
        // Insert the HTML fragment into the results container
        resultsContainer.innerHTML = data.template;

        // Initialize the progress bars
        initializeResultProgressBars();
        if (data.additional_data.focal_lengths.binned.all.length > 0) {
          setShareLink(
            data.additional_data.recommendations_id,
            data.additional_data.style_colours,
          );
          createFocalLengthChart(
            data.additional_data.focal_lengths,
            data.additional_data.style_colours,
          );
          createExposureChart(
            data.additional_data.aperture,
            data.additional_data.iso,
            data.additional_data.shutter_speed,
            data.additional_data.exposure,
            data.additional_data.style_colours,
          );
        }
          setThemeColour(data.additional_data.style_colours);
          enableCollapsingKit();
          initializeTooltips();
          initializeSidebarHighlight();

        var icon = resultsContainer.querySelector("#icon");

        if (data.additional_data.recommendations_id) {
          const recommendations_section_html = fetchLlmRecommendations(data.additional_data.recommendations_id);

        }
      })
      .catch((error) => {
        // --- ERROR ---
        console.error("Error during fetch or processing:", error);
        // Display error message in the results area
        resultsContainer.innerHTML = `<div class="alert alert-danger mt-20px">
                                            <strong>An error occurred:</strong> ${error.message} <br>
                                            Please check the console for more details and try again.
                                          </div>`;
        mainContent.style.display = "block";
        progressContainer.style.display = "none"; // Ensure file progress bar is hidden
      });
  }

  document.dispatchEvent(new Event("custom-ready"));
}

function convertArrayBufferToBinaryString(arrayBuffer, chunkSize = 65536) {
  const bytes = new Uint8Array(arrayBuffer);
  let binaryString = "";
  for (let start = 0; start < bytes.length; start += chunkSize) {
    const chunk = bytes.subarray(start, start + chunkSize);
    binaryString += String.fromCharCode.apply(null, chunk);
  }
  return binaryString;
}

document.addEventListener("DOMContentLoaded", init);

function initializeResultProgressBars() {
  const resultsContainer = document.getElementById("results-container");
  // Find all progress bar containers within the results area
  const progressBarElements = resultsContainer.querySelectorAll(
    ".progress-bar-container",
  );

  progressBarElements.forEach((element) => {
    // Read percentage from the data attribute
    const percentage = parseFloat(element.getAttribute("data-percentage"));
    const targetId = `#${element.id}`; // Use the element's specific ID

    // Check if percentage is valid and ProgressBar library is loaded
    if (!isNaN(percentage) && typeof ProgressBar !== "undefined") {
      // Initialize ProgressBar.Line using options similar to your file progress bar
      // or the options from the previous example - choose what looks best
      var bar = new ProgressBar.Line(targetId, {
        strokeWidth: 4,
        easing: "easeInOut",
        duration: 1400, // Duration for results animation
        color: "#FFEA82", // Start color
        trailColor: "#eee",
        trailWidth: 1,
        svgStyle: { width: "100%", height: "100%" },
        text: {
          // Configuration for displaying text (e.g., percentage)
          style: {
            color: "#777", // Text color
            position: "absolute",
            right: "5px", // Adjust position as needed
            top: "-20px", // Adjust position as needed
            padding: 0,
            margin: 0,
            transform: null,
            fontSize: "0.8em", // Smaller text size
          },
          autoStyleContainer: false,
        },
        from: { color: "#FFEA82" }, // Color transition from
        to: { color: "#ED6A5A" }, // Color transition to
        step: (state, barInstance) => {
          // Use barInstance to avoid scope issues
          // Update text during animation step
          barInstance.setText((barInstance.value() * 100).toFixed(1) + " %");
          // You can also update color based on state if needed
          barInstance.path.setAttribute("stroke", state.color);
        },
      });

      // Animate the bar to the correct percentage (value between 0 and 1)
      bar.animate(percentage / 100.0);
    } else {
      console.warn(
        `Could not initialize result progress bar for ${element.id}. Percentage: ${percentage}, ProgressBar loaded: ${typeof ProgressBar !== "undefined"}`,
      );
      // Optional: Display a fallback if progress bar fails
      element.textContent = `${percentage}% (Progress bar failed to load)`;
    }
  });
}

function setShareLink(recommendations_id, colours) {
  const shareButton = document.getElementById("share-classification-button");
  const modal = document.getElementById("share-modal");
  const previewCanvas = document.getElementById("preview-canvas");
  const downloadBtn = document.getElementById("download-btn");
  const copyLinkBtn = document.getElementById("copy-link-btn");
  const closeModal = document.getElementById("close-modal");
  const shareUrlInput = document.getElementById("share-url");

  // set the input value to the shareable link
  shareUrlInput.value =
    window.location.origin + "/recall/" + recommendations_id;

  shareButton.addEventListener("click", async () => {
    const classificationBox = document.querySelector("#classification-box");
    const footer_height = 100;
    const originalClassificationBoxWidth = classificationBox.style.width;
    const originalClassificationBoxHeight = classificationBox.style.height;
    const originalClassificationBoxPaddingBottom =
      classificationBox.style.paddingBottom;
    const hiddenMpbLogo = document.getElementById("hidden-mpb-logo");

    // Show the modal
    modal.style.display = "flex";

    // Hide the share button
    shareButton.style.display = "none";

    // Resize the classification box before capturing
    classificationBox.style.width = "900px";
    classificationBox.style.height = "900px";
    classificationBox.style.paddingBottom = "150px";

    // Show MPB logo
    hiddenMpbLogo.style.display = "block";

    const canvas = await html2canvas(classificationBox, {
      backgroundColor: null,
    });

    // Put the classification box back to its original size
    classificationBox.style.width = originalClassificationBoxWidth;
    classificationBox.style.height = originalClassificationBoxHeight;
    hiddenMpbLogo.style.display = "none";
    classificationBox.style.paddingBottom =
      originalClassificationBoxPaddingBottom;

    // Copy the entire captured canvas to the preview canvas
    previewCanvas.width = canvas.width;
    previewCanvas.height = canvas.height;
    const ctx = previewCanvas.getContext("2d");
    ctx.drawImage(canvas, 0, 0, canvas.width, canvas.height);

    // footer
    ctx.fillStyle = "rgb(0, 49, 68)";
    ctx.fillRect(0, canvas.height - footer_height, canvas.width, footer_height);
    ctx.fillStyle = "#e83e8c";
    ctx.fillRect(0, canvas.height - footer_height - 10, canvas.width, 10);

    //border
    const borderWidth = 40;
    ctx.strokeStyle = "rgb(0, 49, 68)";
    ctx.lineWidth = borderWidth; // Border width
    ctx.strokeRect(0, 0, canvas.width, canvas.height);

    // Set text styles
    ctx.font = "50px sans-serif";
    ctx.fillStyle = "rgb(255, 209, 103)";

    ctx.textAlign = "left";
    ctx.fillText(
      "What kind of photographer are you?",
      borderWidth,
      canvas.height - 50,
    );

    ctx.textAlign = "right";
    ctx.fillText(
      "mpb.com/1000-words ",
      canvas.width - borderWidth,
      canvas.height - 50,
    );

    // Setup download button
    downloadBtn.onclick = () => {
      const link = document.createElement("a");
      link.download = "photographer_type.png";
      link.href = previewCanvas.toDataURL("image/png");
      link.click();
    };

    // Setup copy link button
    copyLinkBtn.onclick = () => {
      navigator.clipboard
        .writeText(
          "https://www.mpb.com/?utm_source=exif_tool&utm_medium=share&utm_campaign=photographer_type",
        )
        .then(() => alert("Link copied to clipboard!"))
        .catch((err) => alert("Failed to copy link"));
    };

    const shareButtons = [
      document.getElementById("whatsapp-share"),
      document.getElementById("facebook-share"),
      document.getElementById("email-share"),
      document.getElementById("reddit-share"),
    ];

    const shareFile = () => {
      previewCanvas.toBlob((blob) => {
        if (!blob) {
          alert("Failed to create image for sharing.");
          return;
        }
        const file = new File([blob], "photographer_type.png", {
          type: "image/png",
        });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          navigator
            .share({ files: [file], title: "Photographer Type" })
            .catch(() => alert("Sharing failed"));
        } else {
          alert("Sharing is not supported on this browser.");
        }
      });
    };

    shareButtons.forEach((btn) => {
      if (btn) {
        btn.onclick = shareFile;
      }
    });
  });

  closeModal.addEventListener("click", () => {
    modal.style.display = "none";
    shareButton.style.display = "block";
  });
}

// this function is called when the index page is rendered with a recommendations_id
function recallRecommendations(recommendations_id) {
  const resultsContainer = document.getElementById("results-container");
  const progressContainer = document.getElementById("progressContainer"); // For file reading progress
  const mainContent = document.getElementById("main-content"); // The div containing the form

  fetch("/recall/" + recommendations_id, {
    method: "GET",
  })
    .then((response) => {
      // Hide the file reading progress bar container once fetch starts responding
      progressContainer.style.display = "none";

      if (response.ok) {
        return response.text(); // Expect HTML fragment as text
      } else {
        // Try to get error text from response body for better debugging
        return response.text().then((text) => {
          throw new Error(
            `Analysis failed. Server responded with status ${response.status}. ${text || "(No further details)"}`,
          );
        });
      }
    })
    .then((htmlFragment) => {
      // --- SUCCESS ---
      // Check if the response contains a specific error message
      if (htmlFragment === "No recommendations found") {
        resultsContainer.innerHTML = `<div class="alert alert-danger mt-20px">
                                            <strong>No recommendations found:</strong> ${htmlFragment} <br>
                                            Please check the console for more details and try again.
                                          </div>`;
        return;
      }
      resultsContainer.innerHTML = htmlFragment;
      // mainContent.style.display = 'none'; // Keep form hidden

      // Initialize the progress bars *within the results*
      initializeResultProgressBars();
      initializeTooltips();
      initializeSidebarHighlight();
      fetchLlmRecommendations(recommendations_id);
    })
    .catch((error) => {
      // --- ERROR ---
      console.error("Error during fetch or processing:", error);
      // Display error message in the results area
      resultsContainer.innerHTML = `<div class="alert alert-danger mt-20px">
                                        <strong>An error occurred:</strong> ${error.message} <br>
                                        Please check the console for more details and try again.
                                      </div>`;
      // Optionally show the form again
      mainContent.style.display = "block";
      progressContainer.style.display = "none"; // Ensure file progress bar is hidden
    });
}

async function fetchLlmRecommendations(recommendations_id) {
  try {
    const response = await fetch("/llm-recommendations/" + recommendations_id);

    if (!response.ok) {
      throw new Error("Failed to fetch recommendations");
    }

    const htmlFragment = await response.text();

    // Insert the recommendations section HTML into the results container
    // above the element with the id "how-you-can-improve-anchor"
  const recommendationsAnchor = document.getElementById("how-you-can-improve-anchor");
  if (recommendationsAnchor) {
    recommendationsAnchor.insertAdjacentHTML("beforebegin", htmlFragment);
    // Refresh sidebar highlighting now that the section exists
    initializeSidebarHighlight();
  }
  } catch (error) {
    console.error("LLM recommendations error:", error);
  }
}

function createExposureChart(aperture, iso, shutter_speed, exposure, colours) {
  const ctx = document.getElementById("exposureRadarChart").getContext("2d");

  new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Aperture", "ISO Amplitude", "Shutter Speed", "Dark Conditions"],
      datasets: [
        {
          label: "Your Exposure Behavior",
          data: [aperture, iso, shutter_speed, exposure],
          fill: true,
          backgroundColor: colours[0],
          borderColor: "#4f46e5",
          pointBackgroundColor: "#4f46e5",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#4f46e5",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        title: {
          display: false,
          text: "Exposure Profile",
        },
      },
      scales: {
        r: {
          suggestedMin: 0,
          suggestedMax: 50,
          ticks: {
            stepSize: 20,
          },
          pointLabels: {
            font: {
              size: 14,
            },
          },
        },
      },
    },
  });
}

function setThemeColour(colours) {
  // Make all h3 elements the same colour
  const h3Elements = document.querySelectorAll("h3");
  const alerts = document.querySelectorAll(".alert-custom");
  const table_heads = document.querySelectorAll(".table-head");
  const shooting_challenge = document.querySelectorAll(".shooting-challenge");
  const themed_text = document.querySelectorAll(".themed-text");
  const themed = document.querySelectorAll(".themed");

  h3Elements.forEach((h3) => {
    h3.style.color = colours[0];
  });
  alerts.forEach((alert) => {
    alert.style.color = colours[0];
  });
  table_heads.forEach((thead) => {
    thead.style.backgroundColor = colours[0];
    thead.style.color = "white";
  });
  themed_text.forEach((text) => {
    text.style.color = colours[0];
  });
  themed.forEach((themed_element) => {
    themed_element.style.setProperty(
      "background-color",
      colours[0],
      "important",
    );
  });
  shooting_challenge.forEach((challenge) => {
    challenge.style.borderLeft = "5px solid " + colours[0];
  });
}

function enableCollapsingKit() {
  document.querySelectorAll(".toggle-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const targetId = this.getAttribute("data-target");
      const details = document.querySelector(targetId);
      details.classList.toggle("collapse");
    });
  });
}

function initializeTooltips() {
  const tooltipTriggerList = Array.from(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

function createFocalLengthChart(focalLengthData, colours) {
  // Extract labels (category names) and values (frequencies) from the dictionary
  const binned_labels = focalLengthData["binned"]["primes"].map(
    (item) => item[0],
  );
  const binned_primes = focalLengthData["binned"]["primes"].map(
    (item) => item[1],
  );
  const binned_zooms = focalLengthData["binned"]["zooms"].map(
    (item) => item[1],
  );
  const binned_all = focalLengthData["binned"]["all"].map((item) => item[1]);

  const discrete_labels = focalLengthData["discrete"]["zooms"].map(
    (item) => item[0],
  );
  const discrete_primes = focalLengthData["discrete"]["primes"].map(
    (item) => item[1],
  );
  const discrete_zooms = focalLengthData["discrete"]["zooms"].map(
    (item) => item[1],
  );
  const discrete_all = focalLengthData["discrete"]["all"].map(
    (item) => item[1],
  );


  // Get the canvas context for the chart
  const focalLengthChartBinned = document
    .getElementById("focalLengthChartBinned")
    .getContext("2d");
  const focalLengthChartDiscrete = document
    .getElementById("focalLengthChartDiscrete")
    .getContext("2d");

  // Create the bar chart
  new Chart(focalLengthChartBinned, {
    type: "bar",
    data: {
      labels: binned_labels,
      datasets: [
        {
          data: binned_primes,
          label: "Prime Lenses",
          borderWidth: 1,
          backgroundColor: colours[0],
          hidden: false,
        },
        {
          data: binned_zooms,
          label: "Zoom Lenses",
          borderWidth: 1,
          backgroundColor: colours[1],
          hidden: false,
        },
        {
          data: binned_all,
          label: "All Lenses",
          borderWidth: 1,
          backgroundColor: colours[2],
          hidden: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          onClick: (e, legendItem, legend) => {
            const chart = legend.chart;
            const datasetIndex = legendItem.datasetIndex;

            if (datasetIndex === 2) {
              // If "All Lenses" is clicked
              chart.data.datasets[0].hidden = true; // Hide Primes
              chart.data.datasets[1].hidden = true; // Hide Zooms
              chart.data.datasets[2].hidden = false; // Show All Lenses
            } else {
              // If "Prime Lenses" or "Zoom Lenses" is clicked
              chart.data.datasets[0].hidden = false; // Show Primes
              chart.data.datasets[1].hidden = false; // Show Zooms
              chart.data.datasets[2].hidden = true; // Hide All Lenses
            }

            chart.update(); // Update the chart to reflect changes
          },
        },
      },
      scales: {
        x: {
          title: {
            display: false,
            text: "Focal Length Categories",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: false,
            text: "Frequency",
          },
        },
      },
    },
  });
  if (discrete_zooms.length === 0) {
    return;
  }
  // Create the line chart for discrete data
  new Chart(focalLengthChartDiscrete, {
    type: "line",
    data: {
      labels: discrete_labels,
      datasets: [
        // {
        //     data: discrete_primes,
        //     label: 'Prime Lenses',
        //     borderWidth: 1,
        //     backgroundColor: colours[0],
        //     hidden: false,
        // },
        {
          data: discrete_zooms,
          label: "Zoom Lenses",
          borderWidth: 1,
          backgroundColor: colours[1],
          hidden: false,
        },
        // {
        //     data: discrete_all,
        //     label: 'All Lenses',
        //     borderWidth: 1,
        //     backgroundColor: colours[2],
        //     hidden: true,
        // }
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          onClick: (e, legendItem, legend) => {
            const chart = legend.chart;
            const datasetIndex = legendItem.datasetIndex;

            if (datasetIndex === 2) {
              // If "All Lenses" is clicked
              chart.data.datasets[0].hidden = true; // Hide Primes
              chart.data.datasets[1].hidden = true; // Hide Zooms
              chart.data.datasets[2].hidden = false; // Show All Lenses
            } else {
              // If "Prime Lenses" or "Zoom Lenses" is clicked
              chart.data.datasets[0].hidden = false; // Show Primes
              chart.data.datasets[1].hidden = false; // Show Zooms
              chart.data.datasets[2].hidden = true; // Hide All Lenses
            }

            chart.update(); // Update the chart to reflect changes
          },
        },
      },
      scales: {
        x: {
          type: "logarithmic",
          title: {
            display: true,
            text: "Focal Length (mm, log scale)",
          },
          min: discrete_zooms[0][0],
          ticks: {
            callback: function (value) {
              return Number(value).toLocaleString(); // optional: format nicely
            },
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: false,
            text: "Frequency",
          },
        },
      },
    },
  });
  document
    .getElementById("chartSelector")
    .addEventListener("change", function (event) {
      const selectedChart = event.target.value;
      // Toggle visibility based on the selected value
      document.getElementById("binnedChartContainer").style.display =
        selectedChart === "binned" ? "block" : "none";
      document.getElementById("discreteChartContainer").style.display =
        selectedChart === "discrete" ? "block" : "none";
    });
}

let sidebarHighlightHandler = null;

function initializeSidebarHighlight() {
  const ids = [
    "your-classification-anchor",
    "your-current-gear-anchor",
    "how-you-shoot-anchor",
    "what-could-make-your-kit-better-anchor",
    "how-you-can-improve-anchor",
    "thank-you-anchor",
  ];

  const anchors = ids
    .map((id) => document.getElementById(id))
    .filter((el) => el !== null);

  const linkMap = {};
  ids.forEach((id) => {
    const link = document.querySelector(`.sidebar a[href="#${id}"]`);
    if (link) {
      linkMap[id] = link;
    }
  });

  function updateActive() {
    const scrollPos = window.scrollY + 175; // offset for fixed header
    let currentId = anchors.length ? anchors[0].id : null;

    for (let i = 0; i < anchors.length; i++) {
      const start = anchors[i].offsetTop;
      const end =
        i < anchors.length - 1
          ? anchors[i + 1].offsetTop
          : document.body.scrollHeight;
      if (scrollPos >= start && scrollPos < end) {
        currentId = anchors[i].id;
        break;
      }
    }

    ids.forEach((id) => {
      if (linkMap[id]) {
        linkMap[id].classList.toggle("active", id === currentId);
      }
    });
  }

  if (sidebarHighlightHandler) {
    document.removeEventListener("scroll", sidebarHighlightHandler);
    window.removeEventListener("resize", sidebarHighlightHandler);
  }

  sidebarHighlightHandler = updateActive;
  document.addEventListener("scroll", updateActive, { passive: true });
  window.addEventListener("resize", updateActive);
  updateActive();
}
