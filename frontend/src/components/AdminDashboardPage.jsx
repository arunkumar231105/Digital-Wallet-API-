import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api";

export default function AdminDashboardPage() {
  const [depositForm, setDepositForm] = useState({ email: "", amount: "" });
  const [statusEmail, setStatusEmail] = useState("");
  const [freezeEmail, setFreezeEmail] = useState("");
  const [txEmail, setTxEmail] = useState("");
  const [userTransactions, setUserTransactions] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const loadUsers = async () => {
    try {
      const response = await api.get("/admin/users");
      setUsers(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load users");
      if (err.response?.status === 401 || err.response?.status === 403) {
        localStorage.removeItem("token");
        localStorage.removeItem("is_admin");
        navigate("/admin/login");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    let timeoutId;

    const logoutForInactivity = () => {
      localStorage.removeItem("token");
      localStorage.removeItem("is_admin");
      navigate("/login");
    };

    const resetTimer = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(logoutForInactivity, 30000);
    };

    const events = ["mousemove", "mousedown", "keypress", "touchstart", "scroll"];
    events.forEach((eventName) => window.addEventListener(eventName, resetTimer));

    resetTimer();

    return () => {
      clearTimeout(timeoutId);
      events.forEach((eventName) => window.removeEventListener(eventName, resetTimer));
    };
  }, [navigate]);

  const handleAction = async (requestFn, successText) => {
    setWorking(true);
    setError("");
    setMessage("");

    try {
      await requestFn();
      setMessage(successText);
      await loadUsers();
      setDepositForm({ email: "", amount: "" });
      setStatusEmail("");
    } catch (err) {
      setError(err.response?.data?.detail || "Request failed");
    } finally {
      setWorking(false);
    }
  };

  const onDeposit = (event) => {
    event.preventDefault();
    handleAction(() => api.post("/admin/deposit", depositForm), "Deposit successful");
  };

  const onDeactivate = (event) => {
    event.preventDefault();
    handleAction(() => api.post("/admin/deactivate-user", { email: statusEmail }), "User deactivated");
  };

  const onActivate = (event) => {
    event.preventDefault();
    handleAction(() => api.post("/admin/activate-user", { email: statusEmail }), "User activated");
  };

  const onFreeze = (event) => {
    event.preventDefault();
    handleAction(() => api.post("/admin/freeze-user", { user_email: freezeEmail }), "User frozen");
  };

  const onUnfreeze = (event) => {
    event.preventDefault();
    handleAction(() => api.post("/admin/unfreeze-user", { user_email: freezeEmail }), "User unfrozen");
  };

  const onLoadUserTransactions = async (event) => {
    event.preventDefault();
    setWorking(true);
    setError("");
    setMessage("");

    try {
      const response = await api.get(`/admin/user-transactions?email=${encodeURIComponent(txEmail)}`);
      setUserTransactions(response.data);
      setMessage("Loaded user transaction history");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load user transactions");
      setUserTransactions([]);
    } finally {
      setWorking(false);
    }
  };

  const onLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("is_admin");
    navigate("/admin/login");
  };

  if (loading) {
    return (
      <div className="dashboard-shell">
        <div className="card">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-shell">
      <div className="dashboard-grid">
        <section className="card panel-main">
          <header className="top-row">
            <div>
              <h1>Admin Dashboard</h1>
              <p className="subtle">Manage users and balances</p>
            </div>
            <button className="ghost" onClick={onLogout}>
              Logout
            </button>
          </header>

          <div className="actions-grid admin-actions-grid">
            <form className="card mini-card" onSubmit={onDeposit}>
              <h3>Deposit</h3>
              <input
                value={depositForm.email}
                onChange={(e) => setDepositForm((prev) => ({ ...prev, email: e.target.value }))}
                placeholder="User Email"
                type="email"
                required
              />
              <input
                value={depositForm.amount}
                onChange={(e) => setDepositForm((prev) => ({ ...prev, amount: e.target.value }))}
                placeholder="Amount"
                type="number"
                step="0.01"
                required
              />
              <button disabled={working}>{working ? "Processing..." : "Deposit"}</button>
            </form>

            <form className="card mini-card" onSubmit={onDeactivate}>
              <h3>Deactivate User</h3>
              <input value={statusEmail} onChange={(e) => setStatusEmail(e.target.value)} placeholder="User Email" type="email" required />
              <button className="danger" disabled={working}>
                {working ? "Processing..." : "Deactivate"}
              </button>
            </form>

            <form className="card mini-card" onSubmit={onActivate}>
              <h3>Activate User</h3>
              <input value={statusEmail} onChange={(e) => setStatusEmail(e.target.value)} placeholder="User Email" type="email" required />
              <button disabled={working}>{working ? "Processing..." : "Activate"}</button>
            </form>

            <form className="card mini-card" onSubmit={onFreeze}>
              <h3>Freeze User</h3>
              <input value={freezeEmail} onChange={(e) => setFreezeEmail(e.target.value)} placeholder="User Email" type="email" required />
              <button className="danger" disabled={working}>
                {working ? "Processing..." : "Freeze"}
              </button>
            </form>

            <form className="card mini-card" onSubmit={onUnfreeze}>
              <h3>Unfreeze User</h3>
              <input value={freezeEmail} onChange={(e) => setFreezeEmail(e.target.value)} placeholder="User Email" type="email" required />
              <button disabled={working}>{working ? "Processing..." : "Unfreeze"}</button>
            </form>

            <form className="card mini-card" onSubmit={onLoadUserTransactions}>
              <h3>User Transactions</h3>
              <input value={txEmail} onChange={(e) => setTxEmail(e.target.value)} placeholder="User Email" type="email" required />
              <button disabled={working}>{working ? "Processing..." : "Load History"}</button>
            </form>
          </div>

          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
        </section>

        <section className="card panel-table">
          <h2>Users</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Active</th>
                  <th>Admin</th>
                  <th>Frozen</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan="6">No users found</td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{user.is_active ? "Yes" : "No"}</td>
                      <td>{user.is_admin ? "Yes" : "No"}</td>
                      <td>{user.is_frozen ? "Yes" : "No"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="card panel-table">
          <h2>User Transaction History</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {userTransactions.length === 0 ? (
                  <tr>
                    <td colSpan="4">No transactions loaded</td>
                  </tr>
                ) : (
                  userTransactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>{tx.id}</td>
                      <td>{tx.type}</td>
                      <td>{tx.amount}</td>
                      <td>{new Date(tx.timestamp).toLocaleString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
