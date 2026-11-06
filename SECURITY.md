# Security and privacy policy

## Project scope

Voice Health Navigator is an educational local application. It is not a
medical device, clinical service, emergency service, or prescription system.
It must not be used to make treatment or dosing decisions.

## Reporting a concern

Do not post vulnerabilities, private health information, credentials, API
keys, or identifiable audio in a public GitHub issue.

For a security or privacy concern, contact the repository maintainer through a
private GitHub message or the contact method listed on the repository profile.
Include:

1. a short description of the concern;
2. steps to reproduce it without real personal data;
3. the affected file, version, or environment; and
4. the possible impact.

The maintainer should acknowledge the report, assess it privately, and publish
a fix or mitigation when appropriate.

## Safe handling expectations

- Keep ".streamlit/secrets.toml", ".env" files, local models, logs, and
  generated archives out of Git.
- Do not commit recordings, transcripts, answers, or any other personally
  identifiable health information.
- Use only a local development server unless deployment has been independently
  reviewed for privacy, security, and legal requirements.
- Report any route that bypasses emergency wording or medicine/dose guards as
  a high-priority safety issue.
