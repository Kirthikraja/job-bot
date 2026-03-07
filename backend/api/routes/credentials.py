# Credentials API (routes/credentials.py)
#
# This file defines the HTTP endpoints for saving and reading login credentials
# (site, username, password) that the bot uses when it hits a login page.
#
# - POST: Save or update credentials for a site.
#   The client sends site, username, and password. We encrypt the password,
#   then insert or update a row in the credentials table.
#   Used when the user submits their login (e.g. first time the bot needs that site).
#
# - GET: Check if we have credentials for a site, or list all saved sites.
#   With a site (e.g. query param): return that credential (for the bot to log in).
#   Without: return a list of saved sites (e.g. for the UI to show "you have logins for: ...").
#
# Data is stored in the credentials table (Credential model). Encryption/decryption
# of the password is done before save and when the bot needs to use it.
