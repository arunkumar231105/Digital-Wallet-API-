import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../api";

export default function LoginPage() {
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
      const response = await api.post("/auth/login", form);
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("is_admin", "false");
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="card auth-card">
        <h1>Sign In</h1>
        <p className="subtle">Choose your access mode</p>

        <div className="form-stack">
          <button type="button" disabled>
            Login as User
          </button>
          <button type="button" className="ghost" onClick={() => navigate("/admin/login")}>
            Login as Admin
          </button>
        </div>

        <form onSubmit={onSubmit} className="form-stack">
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
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
        <p>
          Need an account? <Link to="/register">Register</Link>
        </p>
        <p>
          Admin access? <Link to="/admin/login">Admin Login</Link>
        </p>
      </div>
    </div>
  );
}
