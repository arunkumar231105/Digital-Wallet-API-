import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../api";

export default function AdminLoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await api.post("/admin/login", form);
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("is_admin", "true");
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Admin login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="card auth-card">
        <h1>Admin Login</h1>
        <p className="subtle">Access admin controls</p>

        <form onSubmit={onSubmit} className="form-stack">
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
            {loading ? "Signing in..." : "Admin Login"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
        <p>
          Need admin account? <Link to="/admin-register">Admin Register</Link>
        </p>
        <p>
          User login? <Link to="/login">Go to Login</Link>
        </p>
      </div>
    </div>
  );
}
