document.addEventListener('DOMContentLoaded', function() {
    const input = document.querySelector('input[name="query"]');
    const suggestionBox = document.createElement('div');
    suggestionBox.className = 'suggestion-box';
    input.parentNode.appendChild(suggestionBox);

    let lastValue = '';
    let controller = null;

    input.addEventListener('input', function() {
        // Do NOT trim, allow spaces to be part of the query
        const value = input.value;
        // Only skip fetch if value is identical to lastValue AND suggestionBox is already visible
        if (value === lastValue && suggestionBox.style.display === 'block') {
            return;
        }
        lastValue = value;
        if (controller) controller.abort();
        controller = new AbortController();
        fetch('/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ partial: value }),
            signal: controller.signal
        })
        .then(r => r.json())
        .then(data => {
            suggestionBox.innerHTML = '';
            if (data.suggestions && data.suggestions.length > 0) {
                data.suggestions.forEach(s => {
                    const div = document.createElement('div');
                    div.className = 'suggestion';
                    div.textContent = s;
                    div.onclick = () => {
                        input.value = s;
                        suggestionBox.innerHTML = '';
                        suggestionBox.style.display = 'none';
                    };
                    suggestionBox.appendChild(div);
                });
                suggestionBox.style.display = 'block';
            } else {
                suggestionBox.style.display = 'none';
            }
        })
        .catch(() => {
            suggestionBox.innerHTML = '';
            suggestionBox.style.display = 'none';
        });
    });

    document.addEventListener('click', function(e) {
        if (!suggestionBox.contains(e.target) && e.target !== input) {
            suggestionBox.innerHTML = '';
            suggestionBox.style.display = 'none';
        }
    });
});
