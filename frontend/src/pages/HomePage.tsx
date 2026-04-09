import { useEffect, useState } from "react";
import { Button, Flex, Spin, Typography } from "antd";
import { Navigate, useNavigate } from "react-router-dom";
import { getMonthSummary } from "../api/monthSummary";
import { AUTH_TOKEN_KEY } from "../constants/auth";

export default function HomePage() {
  const navigate = useNavigate();
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const [monthTotal, setMonthTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    const authToken = token;
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getMonthSummary(authToken);
        if (!cancelled) {
          setMonthTotal(data.current_month_total);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Ошибка загрузки");
          setMonthTotal(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const logout = () => {
    localStorage.clear();
    navigate("/login", { replace: true });
  };

  const formatted =
    monthTotal === null
      ? null
      : new Intl.NumberFormat("ru-RU", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }).format(monthTotal);

  return (
    <Flex
      vertical
      gap={16}
      align="center"
      justify="center"
      style={{ minHeight: "100vh" }}
    >
      <span style={{ fontSize: 18 }}>Ну здарова, Николай мужичара!</span>
      {loading ? (
        <Spin />
      ) : error ? (
        <Typography.Text type="danger">{error}</Typography.Text>
      ) : (
        <span style={{ fontSize: 22, fontWeight: 600 }}>
          В этом месяце вы наколотили {formatted} рублей!
        </span>
      )}
      <Button onClick={logout}>Выйти</Button>
    </Flex>
  );
}
