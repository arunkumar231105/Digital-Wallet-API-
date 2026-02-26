import { Navigate, Route, Routes } from "react-router-dom";

import AdminDashboardPage from "./components/AdminDashboardPage";
import AdminLoginPage from "./components/AdminLoginPage";
import AdminRegisterPage from "./components/AdminRegisterPage";
import DashboardPage from "./components/DashboardPage";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
}

function AdminPrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  const isAdmin = localStorage.getItem("is_admin") === "true";
  return token && isAdmin ? children : <Navigate to="/admin/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/admin/login" element={<AdminLoginPage />} />
      <Route path="/admin-register" element={<AdminRegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <DashboardPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin/dashboard"
        element={
          <AdminPrivateRoute>
            <AdminDashboardPage />
          </AdminPrivateRoute>
        }
      />
    </Routes>
  );
}
