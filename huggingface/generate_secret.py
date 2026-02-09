#!/usr/bin/env python3
"""
Generate a secure random secret for BETTER_AUTH_SECRET
"""
import secrets

print("🔐 Generating secure random secret...\n")

secret = secrets.token_urlsafe(32)

print("Your BETTER_AUTH_SECRET:")
print("=" * 60)
print(secret)
print("=" * 60)
print("\nCopy this value and use it in your .env file:")
print(f"BETTER_AUTH_SECRET={secret}")
print("\n⚠️  Keep this secret safe and never commit it to git!")
