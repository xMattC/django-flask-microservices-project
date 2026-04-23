# Productivity / Work Management Platform (Microservices Project)

## Overview

A work management platform for small teams where users can:
- Manage tasks
- Clock in and out of work sessions
- Receive reminders
- View productivity reports

### Architecture

- **Django (web)** → frontend, authentication, dashboard
- **Flask services** → focused backend microservices

---

## Service Structure

```text
repo/
  web/
  tasks/
  time-tracking/
  notifications/
  reports/
  docs/
  docker-compose.yml
  README.md
```

---

## Service Responsibilities

### web/ (Django)

Handles:
- User registration/login/logout
- User profiles
- Dashboard UI
- Task pages
- Clock-in / clock-out UI
- Reports UI
- Calls backend services via APIs

---

### tasks/ (Flask)

Handles:
- Create tasks
- Update tasks
- Assign tasks
- Set due dates
- Mark complete

Task states:
- todo
- in_progress
- blocked
- done

---

### time-tracking/ (Flask)

Handles:
- Clock in
- Clock out
- Active session tracking
- Session history
- Total hours worked

Core rules:
- One active session per user
- Clock-out closes session
- Duration calculated by service

---

### notifications/ (Flask)

Handles:
- Task reminders
- Clock-out reminders
- Daily summaries
- Mock email sending

---

### reports/ (Flask)

Handles:
- Daily summaries
- Weekly summaries
- Task completion stats
- Productivity overview

---

## MVP Scope

### Django
- Auth (login/register)
- Dashboard
- Pages for tasks, time tracking, reports

### Tasks Service
- Create task
- List tasks
- Update task status

### Time Tracking Service
- Clock in
- Clock out
- View today’s sessions

### Notifications Service
- Basic reminders

### Reports Service
- Weekly hours total
- Completed tasks count

---

## Architecture Principles

- Each service is independently deployable
- Each service owns its own business logic
- Services communicate via APIs
- No shared business logic between services
- Django does NOT own domain logic for services

---

## Example User Flow

1. User signs up (Django)
2. Creates a task (Tasks service)
3. Clocks in (Time Tracking service)
4. Works on task
5. Clocks out
6. Receives notification
7. Views report

---

## Future Enhancements

- Link time entries to tasks
- Advanced notifications
- Charts in reports
- Team-level dashboards
- Project grouping

---

## Notes

- Keep services focused
- Avoid over-engineering
- Prioritise clean boundaries over complexity

---

## Suggested Project Names

- WorkPulse
- FlowTrack
- TeamClock
- TaskForge
- WorkBoard

---

## Summary

This project demonstrates:
- Microservice architecture principles
- Clear service boundaries
- Independent deployment capability
- Realistic product design

The goal is to show understanding, not just implementation.

