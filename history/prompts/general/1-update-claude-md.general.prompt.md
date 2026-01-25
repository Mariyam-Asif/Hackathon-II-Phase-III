---
id: 1
title: Update CLAUDE.md for Todo Full-Stack Web Application
stage: general
date_iso: 2026-01-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: Update CLAUDE.md file with project requirements
labels: ["configuration", "documentation", "project-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - C:\Users\mariy\OneDrive\Desktop\Hackathon II\CLAUDE.md
tests_yaml: []
---

# Update CLAUDE.md for Todo Full-Stack Web Application

## Prompt Text
Update the `claude.md` file based on my project requirements. In this file:
- Use Auth Agent for authentication.
- Use Frontend Agent for frontend development (e.g. Next.js)
- Use DB Agent for database design and operations.
- Use Backend Agent for FastAPI development.

Below are my project requirements:

"""
Phase II: Todo Full-Stack Web Application
Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern multi-user web application with persistent storage.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.
Requirements
Implement all 5 Basic Level features as a web application
Create RESTful API endpoints
Build responsive frontend interface
Store data in Neon Serverless PostgreSQL database
Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer
Technology
Frontend
Next.js 16+ (App Router)
Backend
Python FastAPI
ORM
SQLModel
Database
Neon Serverless PostgreSQL
Spec-Driven
Claude Code + Spec-Kit Plus
Authentication
Better Auth

Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.
How It Works
User logs in on Frontend → Better Auth creates a session and issues a JWT token
Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
Backend receives request → Extracts token from header, verifies signature using shared secret
Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
Backend filters data → Returns only tasks belonging to that user
"""

## Response Text
Updated the CLAUDE.md file to include project-specific instructions for the Todo Full-Stack Web Application with the following changes:

1. Added project-specific instructions section with agent usage guidelines
2. Included technology stack information (Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
3. Documented the Better Auth JWT authentication flow with 5-step process
4. Updated architect guidelines to reflect the Todo application requirements
5. Enhanced the basic project structure section with detailed directory structure

The updated file now provides clear guidance on which agents to use for specific tasks:
- Auth Agent for authentication implementation using Better Auth
- Frontend Agent for Next.js development
- DB Agent for database operations with Neon Serverless PostgreSQL and SQLModel
- Backend Agent for FastAPI development

## Outcome
Successfully updated the CLAUDE.md file to reflect the requirements for the Todo Full-Stack Web Application project, including proper agent usage, technology stack details, authentication flow, and architectural guidelines.