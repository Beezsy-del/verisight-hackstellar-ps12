# Security audit and implementation

Validated byte/format/dimension limits are retained from Hackstellar. The API rejects excessive concurrent work explicitly and bounds output transport. Evidence-invalid reports cannot leave analysis APIs as successful assessments; no settlement or automatic release approval is provided.

The legacy server.py was investigated: it served the repository root and used a global evidence listing. It is replaced with a compatibility launcher for the maintained FastAPI application, bound to loopback. Its separate unprotected storage/API are retired; maintained mobile/session workflows remain. This avoids exposing arbitrary repository files through that launcher.

Secrets remain environment-only; no credentials or original data are committed/copied into the new project. Private Supabase storage and UUID bearer sessions are retained. Application-level account authentication, deployment rate controls, dedicated retention scheduler and authenticated history are not claimed implemented. Do not expose this prototype as a certified multi-tenant service without those controls and deployment validation. Optional features are not fabricated: no bank/PSP verification, trusted C2PA signature validation, threat-intelligence feed or validated forgery model is represented as active.

No original repository was modified. Original and unified testing uses synthetic fixtures. Known limitations and inherited storage retention constraints are explicit in KNOWN_LIMITATIONS.md.
