# Variables file for the environment system-albatross.tfvars

# Settings for user interview
# Uncomment min_scale & external_allow_list vars to ensure albatross is always ready with a running container, and to allow access from the entire web.

# These settings can be toggled by the project maintainer at will in preparation for an interview, 
# but should be enabled & disabled promptly in the hours before and after.

# Firewall changes (external_allow_list) can take ~15 minutes to propogate.
# min_scale=1
# external_allow_list =["0.0.0.0/0"]