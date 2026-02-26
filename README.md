# 💳 Simple Digital Wallet API

A production-style backend wallet system built with FastAPI, PostgreSQL, Redis, JWT authentication, and Docker.

This project demonstrates real-world backend engineering concepts including atomic transactions, idempotency, role-based access control, caching, transaction limits, and background processing.

---

## 🚀 Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- JWT Authentication
- Docker & Docker Compose
- SMTP Email Integration

---

## 🔐 Authentication System

- User Registration & Login
- Admin Registration & Login
- JWT Protected Routes
- Role-Based Access Control
- 30-Second Session Timeout (Auto Logout)

---

## 👤 User Features

Users can:

- Withdraw money
- Transfer money
- View transaction history
- Deactivate their own account

Users cannot:

- Deposit money
- Reactivate their account
- Bypass daily transaction limits

---

## 🛠 Admin Features

Admin has full system control.

Admin can:

- Deposit money to any user
- Freeze any account
- Unfreeze any account
- Activate any user
- Deactivate any user
- View any user's transaction history

Email notifications are sent when:

- Admin deposits funds
- Admin freezes an account
- Admin unfreezes an account

---

## 💰 Wallet Logic

- Each user has exactly one wallet
- One-to-one relationship between User and Wallet

### Transaction Types

- `deposit`
- `withdraw`
- `transfer_out`
- `transfer_in`

Transaction history shows:

- ID
- Type
- Counterparty Name
- Amount
- Status (SUCCESS / FAILED)
- Timestamp

---

## ⚙ Advanced Backend Concepts Implemented

### 1️⃣ Atomic Transactions

All financial operations run inside a single database transaction block.

If any error occurs:
- Entire operation rolls back
- No partial balance updates

---

### 2️⃣ Idempotency Key

Transfer and withdraw require:
Idempotency-Key header


Prevents:
- Duplicate transactions
- Double spending
- Rapid repeated submissions

One request = One execution.

---

### 3️⃣ Daily Transaction Limits

Per user per day:

- Maximum $100 withdraw
- Maximum $100 transfer

Limit resets automatically the next day.

---

### 4️⃣ Redis Caching

Used for:

- Wallet balance caching
- Transaction history caching

Reduces database load and improves performance.

---

### 5️⃣ FastAPI Background Tasks

Used for:

- Sending email notifications
- Logging transaction results

Non-blocking execution.

---

### 6️⃣ Transaction Logging

Each transaction records:

- SUCCESS
- FAILED
- Failure reason

Provides full audit trail.

---

### 7️⃣ Account Freeze System

If account is frozen:

- Withdraw blocked
- Transfer blocked
- Deposit blocked

Admin required to unfreeze.

---

## 📬 Email Notifications

SMTP integration using Gmail App Password.

Emails sent for:

- Transfer received
- Admin deposit
- Account freeze
- Account unfreeze

---

## 📦 Running With Docker

```bash
docker compose up --build


Prevents:
- Duplicate transactions
- Double spending
- Rapid repeated submissions

One request = One execution.

---

### 3️⃣ Daily Transaction Limits

Per user per day:

- Maximum $100 withdraw
- Maximum $100 transfer

Limit resets automatically the next day.

---

### 4️⃣ Redis Caching

Used for:

- Wallet balance caching
- Transaction history caching

Reduces database load and improves performance.

---

### 5️⃣ FastAPI Background Tasks

Used for:

- Sending email notifications
- Logging transaction results

Non-blocking execution.

---

### 6️⃣ Transaction Logging

Each transaction records:

- SUCCESS
- FAILED
- Failure reason

Provides full audit trail.

---

### 7️⃣ Account Freeze System

If account is frozen:

- Withdraw blocked
- Transfer blocked
- Deposit blocked

Admin required to unfreeze.

---

## 📬 Email Notifications

SMTP integration using Gmail App Password.

Emails sent for:

- Transfer received
- Admin deposit
- Account freeze
- Account unfreeze

---

## 📦 Running With Docker

```bash
docker compose up --build

Backend:
http://localhost:8000

Frontend:
http://localhost:3000

backend/
  app/
    routes/
    utils/
    models.py
    auth.py
    database.py
frontend/
docker-compose.yml
