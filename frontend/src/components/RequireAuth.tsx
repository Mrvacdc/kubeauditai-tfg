import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { setAuthToken } from "../api/kubeauditApi";

type RequireAuthProps = {
  children: ReactNode;
};

export default function RequireAuth({ children }: RequireAuthProps) {
  const token = localStorage.getItem("kubeaudit_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  setAuthToken(token);

  return <>{children}</>;
}
