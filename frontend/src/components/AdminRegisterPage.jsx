import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../api";

export default function AdminRegisterPage() {
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
      await api.post("/admin/register", form);
      setMessage("Admin registered successfully. Continue to admin login.");
      setTimeout(() => navigate("/admin/login"), 900);
    } catch (err) {
      setError(err.response?.data?.detail || "Admin registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="card auth-card">
        <h1>Admin Register</h1>
        <p className="subtle">Create an admin account</p>

        <form onSubmit={onSubmit} className="form-stack">
          <input name="name" placeholder="Admin Name" value={form.name} onChange={onChange} required />
          <input name="email" type="email" placeholder="Admin Email" value={form.email} onChange={onChange} required />
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={onChange}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Registering..." : "Register Admin"}
          </button>
        </form>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}

        <p>
          Already have admin access? <Link to="/admin/login">Admin Login</Link>
        </p>
      </div>
    </div>
  );
}
