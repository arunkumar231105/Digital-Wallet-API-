import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../api";

export default function RegisterPage() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    try {
      await api.post("/auth/register", form);
      setMessage("Registration successful. Please log in.");
      setTimeout(() => navigate("/login"), 900);
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="card auth-card">
        <h1>Create Account</h1>
        <p className="subtle">Simple Digital Wallet API</p>

        <form onSubmit={onSubmit} className="form-stack">
          <input name="name" placeholder="Full name" value={form.name} onChange={onChange} required />
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={onChange} required />
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={onChange}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <p>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
