#!/usr/bin/env python3
"""
UNIFIND Backend - Startup Validation Script

This script validates that all required services and configurations are available
before starting the application. It performs comprehensive checks and fails fast
if any critical dependency is unavailable.

Usage:
    python scripts/startup_validation.py

Exit Codes:
    0 - All checks passed
    1 - Critical check failed
    2 - Configuration error
"""
import logging
import os
import sys
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class StartupValidator:
    """Validates all startup requirements."""

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.results: List[Tuple[str, bool, str]] = []

    def check(self, name: str, condition: bool, message: str, critical: bool = True):
        """Record a check result."""
        if condition:
            self.checks_passed += 1
            logger.info(f"✅ {name}: PASS")
            self.results.append((name, True, message))
        else:
            if critical:
                self.checks_failed += 1
                logger.error(f"❌ {name}: FAIL - {message}")
                self.results.append((name, False, message))
            else:
                self.warnings += 1
                logger.warning(f"⚠️  {name}: WARNING - {message}")
                self.results.append((name, False, message))

        return condition

    def validate_environment_variables(self) -> bool:
        """Validate all required environment variables are set."""
        logger.info("=" * 60)
        logger.info("PHASE 1: Environment Variable Validation")
        logger.info("=" * 60)

        required_vars = {
            # Firebase
            "FIREBASE_PROJECT_ID": "Firebase project identifier",
            "FIREBASE_PRIVATE_KEY_ID": "Firebase private key ID",
            "FIREBASE_PRIVATE_KEY": "Firebase service account private key",
            "FIREBASE_CLIENT_EMAIL": "Firebase service account email",
            "FIREBASE_CLIENT_ID": "Firebase client ID",
            "FIREBASE_CLIENT_CERT_URL": "Firebase client certificate URL",
            # AI
            "GEMINI_API_KEY": "Google Gemini API key for AI features",
            # Storage
            "CLOUDINARY_CLOUD_NAME": "Cloudinary cloud name",
            "CLOUDINARY_API_KEY": "Cloudinary API key",
            "CLOUDINARY_API_SECRET": "Cloudinary API secret",
            # Email
            "GMAIL_USER": "Gmail account for sending emails",
            "GMAIL_APP_PASSWORD": "Gmail app password",
            # Configuration
            "CORS_ORIGINS": "Allowed CORS origins",
            "ENVIRONMENT": "Application environment (development/staging/production)",
        }

        all_present = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value or value.strip() == "":
                self.check(
                    f"ENV: {var}",
                    False,
                    f"Missing required environment variable: {description}",
                    critical=True,
                )
                all_present = False
            else:
                # Mask sensitive values in logs
                if "KEY" in var or "PASSWORD" in var or "SECRET" in var:
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    display_value = value[:50] + "..." if len(value) > 50 else value

                self.check(f"ENV: {var}", True, f"Set to: {display_value}", critical=True)

        return all_present

    def validate_environment_format(self) -> bool:
        """Validate environment variable formats."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 2: Environment Format Validation")
        logger.info("=" * 60)

        all_valid = True

        # Validate ENVIRONMENT value
        env = os.getenv("ENVIRONMENT", "development")
        valid_envs = ["development", "staging", "production", "test"]
        self.check(
            "ENV FORMAT: ENVIRONMENT",
            env in valid_envs,
            f"Must be one of: {', '.join(valid_envs)}. Got: {env}",
            critical=True,
        )
        if env not in valid_envs:
            all_valid = False

        # Validate Firebase private key format
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
        self.check(
            "ENV FORMAT: FIREBASE_PRIVATE_KEY",
            private_key.startswith("-----BEGIN PRIVATE KEY-----"),
            "Must start with '-----BEGIN PRIVATE KEY-----'",
            critical=True,
        )
        if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
            all_valid = False

        # Validate email format
        gmail_user = os.getenv("GMAIL_USER", "")
        self.check(
            "ENV FORMAT: GMAIL_USER",
            "@" in gmail_user and "." in gmail_user,
            "Must be a valid email address",
            critical=True,
        )
        if not ("@" in gmail_user and "." in gmail_user):
            all_valid = False

        # Validate CORS origins
        cors_origins = os.getenv("CORS_ORIGINS", "")
        origins = [o.strip() for o in cors_origins.split(",")]

        # Check for wildcard in production
        if env == "production" and "*" in cors_origins:
            self.check(
                "ENV FORMAT: CORS_ORIGINS",
                False,
                "Wildcard (*) not allowed in production",
                critical=True,
            )
            all_valid = False
        else:
            self.check(
                "ENV FORMAT: CORS_ORIGINS",
                True,
                f"Configured {len(origins)} origin(s)",
                critical=True,
            )

        # Warn about non-HTTPS origins in production
        if env == "production":
            for origin in origins:
                if not origin.startswith("https://") and not origin.startswith("http://localhost"):
                    self.check(
                        f"ENV SECURITY: CORS origin {origin}",
                        False,
                        "Non-HTTPS origin in production is a security risk",
                        critical=False,
                    )

        return all_valid

    def validate_firebase_connection(self) -> bool:
        """Validate Firebase connection."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 3: Firebase Connection Validation")
        logger.info("=" * 60)

        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            # Check if already initialized
            try:
                firebase_admin.get_app()
                logger.info("Firebase already initialized")
                app = firebase_admin.get_app()
            except ValueError:
                # Initialize Firebase
                cred_dict = {
                    "type": os.getenv("FIREBASE_TYPE", "service_account"),
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv(
                        "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
                    ),
                    "token_uri": os.getenv(
                        "FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"
                    ),
                    "auth_provider_x509_cert_url": os.getenv(
                        "FIREBASE_AUTH_PROVIDER_CERT_URL",
                        "https://www.googleapis.com/oauth2/v1/certs",
                    ),
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
                }

                cred = credentials.Certificate(cred_dict)
                app = firebase_admin.initialize_app(cred)

            self.check(
                "FIREBASE: Initialization",
                True,
                "Firebase Admin SDK initialized successfully",
                critical=True,
            )

            # Test Firestore connection
            db = firestore.client()

            # Try to access a collection (this will fail if credentials are invalid)
            try:
                # Use a lightweight operation
                _ = db.collection("_startup_validation").limit(1).get()
                self.check(
                    "FIREBASE: Firestore Connection",
                    True,
                    "Successfully connected to Firestore",
                    critical=True,
                )
                return True
            except Exception as e:
                self.check(
                    "FIREBASE: Firestore Connection",
                    False,
                    f"Failed to connect to Firestore: {str(e)}",
                    critical=True,
                )
                return False

        except ImportError as e:
            self.check(
                "FIREBASE: Dependencies",
                False,
                f"Firebase Admin SDK not installed: {str(e)}",
                critical=True,
            )
            return False
        except Exception as e:
            self.check(
                "FIREBASE: Initialization",
                False,
                f"Failed to initialize Firebase: {str(e)}",
                critical=True,
            )
            return False

    def validate_gemini_api(self) -> bool:
        """Validate Gemini API connection."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 4: Gemini AI API Validation")
        logger.info("=" * 60)

        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.check("GEMINI: API Key", False, "GEMINI_API_KEY not set", critical=True)
                return False

            # Configure Gemini
            genai.configure(api_key=api_key)

            self.check(
                "GEMINI: Configuration", True, "Gemini API configured successfully", critical=True
            )

            # Test API by listing models (lightweight operation)
            try:
                models = list(genai.list_models())
                self.check(
                    "GEMINI: API Connection",
                    len(models) > 0,
                    f"Successfully connected to Gemini API ({len(models)} models available)",
                    critical=True,
                )
                return True
            except Exception as e:
                self.check(
                    "GEMINI: API Connection",
                    False,
                    f"Failed to connect to Gemini API: {str(e)}",
                    critical=True,
                )
                return False

        except ImportError as e:
            self.check(
                "GEMINI: Dependencies", False, f"Gemini SDK not installed: {str(e)}", critical=True
            )
            return False
        except Exception as e:
            self.check(
                "GEMINI: Configuration",
                False,
                f"Failed to configure Gemini: {str(e)}",
                critical=True,
            )
            return False

    def validate_cloudinary(self) -> bool:
        """Validate Cloudinary configuration."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 5: Cloudinary Storage Validation")
        logger.info("=" * 60)

        try:
            import cloudinary

            # Configure Cloudinary
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET"),
                secure=True,
            )

            self.check(
                "CLOUDINARY: Configuration",
                True,
                "Cloudinary configured successfully",
                critical=True,
            )

            # Test connection by pinging API
            try:
                from cloudinary import api

                result = api.ping()
                self.check(
                    "CLOUDINARY: API Connection",
                    result.get("status") == "ok",
                    "Successfully connected to Cloudinary API",
                    critical=True,
                )
                return True
            except Exception as e:
                self.check(
                    "CLOUDINARY: API Connection",
                    False,
                    f"Failed to connect to Cloudinary: {str(e)}",
                    critical=True,
                )
                return False

        except ImportError as e:
            self.check(
                "CLOUDINARY: Dependencies",
                False,
                f"Cloudinary SDK not installed: {str(e)}",
                critical=True,
            )
            return False
        except Exception as e:
            self.check(
                "CLOUDINARY: Configuration",
                False,
                f"Failed to configure Cloudinary: {str(e)}",
                critical=True,
            )
            return False

    def validate_python_environment(self) -> bool:
        """Validate Python environment."""
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 6: Python Environment Validation")
        logger.info("=" * 60)

        # Check Python version
        import sys

        version = sys.version_info
        required_version = (3, 11)

        self.check(
            "PYTHON: Version",
            version >= required_version,
            f"Python {version.major}.{version.minor}.{version.micro} "
            f"(required: {required_version[0]}.{required_version[1]}+)",
            critical=True,
        )

        # Check critical packages
        critical_packages = [
            "fastapi",
            "uvicorn",
            "gunicorn",
            "firebase_admin",
            "google.generativeai",
            "cloudinary",
            "pydantic",
        ]

        all_installed = True
        for package in critical_packages:
            try:
                __import__(package)
                self.check(f"PYTHON: Package {package}", True, "Installed", critical=True)
            except ImportError:
                self.check(f"PYTHON: Package {package}", False, "Not installed", critical=True)
                all_installed = False

        return all_installed and version >= required_version

    def print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)

        total_checks = self.checks_passed + self.checks_failed + self.warnings

        logger.info(f"Total Checks: {total_checks}")
        logger.info(f"✅ Passed: {self.checks_passed}")
        logger.info(f"❌ Failed: {self.checks_failed}")
        logger.info(f"⚠️  Warnings: {self.warnings}")

        if self.checks_failed > 0:
            logger.error("\n❌ STARTUP VALIDATION FAILED")
            logger.error("The application cannot start safely with the current configuration.")
            logger.error("Please fix the issues above and try again.")
            return False
        elif self.warnings > 0:
            logger.warning("\n⚠️  STARTUP VALIDATION PASSED WITH WARNINGS")
            logger.warning("The application can start, but there are configuration issues.")
            logger.warning("Please review the warnings above.")
            return True
        else:
            logger.info("\n✅ STARTUP VALIDATION PASSED")
            logger.info("All checks passed. The application is ready to start.")
            return True

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        logger.info("=" * 60)
        logger.info("UNIFIND BACKEND - STARTUP VALIDATION")
        logger.info("=" * 60)
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Python: {sys.version}")
        logger.info("=" * 60)

        # Run all validation phases
        self.validate_python_environment()
        self.validate_environment_variables()
        self.validate_environment_format()
        self.validate_firebase_connection()
        self.validate_gemini_api()
        self.validate_cloudinary()

        # Print summary
        return self.print_summary()


def main():
    """Main entry point."""
    validator = StartupValidator()

    try:
        success = validator.run_all_validations()

        if success:
            if validator.warnings > 0:
                sys.exit(0)  # Success with warnings
            else:
                sys.exit(0)  # Complete success
        else:
            sys.exit(1)  # Validation failed

    except KeyboardInterrupt:
        logger.error("\n\nValidation interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"\n\nUnexpected error during validation: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
