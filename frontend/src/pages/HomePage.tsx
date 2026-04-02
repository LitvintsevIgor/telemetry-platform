import { Button, Flex } from "antd";
import { Navigate, useNavigate } from "react-router-dom";
import { AUTH_TOKEN_KEY } from "../constants/auth";

export default function HomePage() {
  const navigate = useNavigate();
  const token = localStorage.getItem(AUTH_TOKEN_KEY);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const logout = () => {
    localStorage.clear();
    navigate("/login", { replace: true });
  };

  return (
    <Flex
      vertical
      gap={16}
      align="center"
      justify="center"
      style={{ minHeight: "100vh" }}
    >
      <span style={{ fontSize: 18 }}>Ну здарова, Николай мужичара!</span>
      <Button onClick={logout}>Выйти</Button>
    </Flex>
  );
}
