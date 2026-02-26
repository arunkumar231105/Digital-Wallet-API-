import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api";

function toCurrency(value) {
  const numeric = Number(value || 0);
  return numeric.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function DashboardPage() {
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const [transferAmount, setTransferAmount] = useState("");
  const [transferEmail, setTransferEmail] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const computedBalance = useMemo(() => {
    if (transactions.length === 0) {
      return Number(balance || 0);
    }

    return transactions.reduce((sum, tx) => {
      const txAmount = Number(tx.amount);
      if (tx.type === "deposit" || tx.type === "transfer_in") {
        return sum + txAmount;
      }
      return sum - txAmount;
    }, 0);
  }, [transactions, balance]);

  const loadWallet = async () => {
    setLoading(true);
    setError("");

    try {
      const walletRes = await api.post("/wallet/create");
      setBalance(walletRes.data.balance || 0);

      const txRes = await api.get("/wallet/transactions");
      setTransactions(txRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load wallet");
      if (err.response?.status === 401) {
        localStorage.removeItem("token");
        navigate("/login");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWallet();
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

  const executeAction = async (requestFn, successText) => {
    if (working) {
      return;
    }
    setWorking(true);
    setError("");
    setMessage("");

    try {
      const response = await requestFn();
      if (response.data?.balance !== undefined) {
        setBalance(response.data.balance);
      }
      setMessage(successText);
      const txRes = await api.get("/wallet/transactions");
      setTransactions(txRes.data);
      setWithdrawAmount("");
      setTransferAmount("");
    } catch (err) {
      setError(err.response?.data?.detail || "Action failed");
    } finally {
      setWorking(false);
    }
  };

  const onWithdraw = (event) => {
    event.preventDefault();
    if (working) {
      return;
    }
    executeAction(() => api.post("/wallet/withdraw", { amount: withdrawAmount }), "Withdraw successful");
  };

  const onTransfer = (event) => {
    event.preventDefault();
    if (working) {
      return;
    }
    executeAction(() => api.post("/wallet/transfer", { email: transferEmail, amount: transferAmount }), "Transfer successful");
  };

  const onDeactivate = async () => {
    setWorking(true);
    setError("");
    setMessage("");

    try {
      await api.post("/users/deactivate");
      localStorage.removeItem("token");
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to deactivate account");
    } finally {
      setWorking(false);
    }
  };

  const onLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("is_admin");
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="dashboard-shell">
        <div className="card">Loading wallet...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-shell">
      <div className="dashboard-grid">
        <section className="card panel-main">
          <header className="top-row">
            <div>
              <h1>Wallet Dashboard</h1>
              <p className="subtle">Manage your funds securely</p>
            </div>
            <button className="ghost" onClick={onLogout}>
              Logout
            </button>
          </header>

          <div className="balance-box">
            <span>Current Balance</span>
            <strong>${toCurrency(computedBalance)}</strong>
          </div>

          <div className="actions-grid">
            <form className="card mini-card" onSubmit={onWithdraw}>
              <h3>Withdraw</h3>
              <input
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                placeholder="Amount"
                type="number"
                step="0.01"
                required
              />
              <button disabled={working}>{working ? "Processing..." : "Withdraw"}</button>
            </form>

            <form className="card mini-card" onSubmit={onTransfer}>
              <h3>Transfer</h3>
              <input value={transferEmail} onChange={(e) => setTransferEmail(e.target.value)} placeholder="Recipient Email" type="email" required />
              <input
                value={transferAmount}
                onChange={(e) => setTransferAmount(e.target.value)}
                placeholder="Amount"
                type="number"
                step="0.01"
                required
              />
              <button disabled={working}>{working ? "Processing..." : "Transfer"}</button>
            </form>
          </div>

          <button className="danger" onClick={onDeactivate} disabled={working}>
            Deactivate Account
          </button>

          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
        </section>

        <section className="card panel-table">
          <h2>Transaction History</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Counterparty</th>
                  <th>Amount</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan="5">No transactions found</td>
                  </tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>{tx.id}</td>
                      <td>
                        {tx.type === "transfer_out"
                          ? `Transferred to ${tx.counterparty_name || ""}`
                          : tx.type === "transfer_in"
                            ? `Received from ${tx.counterparty_name || ""}`
                            : tx.type}
                      </td>
                      <td>{tx.counterparty_name || "-"}</td>
                      <td>${toCurrency(tx.amount)}</td>
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
