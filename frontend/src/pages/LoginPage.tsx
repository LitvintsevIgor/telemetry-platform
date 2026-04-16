import { Button, Card, ConfigProvider, Form, Input, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useLoginMutation } from '../hooks/useLoginMutation'
import { AUTH_TOKEN_KEY } from '../constants/auth'
import styles from './LoginPage.module.css'

const loginTheme = {
  token: {
    colorPrimary: '#007aff',
    borderRadiusLG: 12,
  },
  components: {
    Form: {
      labelColor: 'rgba(60, 60, 67, 0.6)',
      labelFontSize: 13,
      verticalLabelPadding: '0 0 6px',
    },
    Input: {
      borderRadius: 12,
      paddingBlockLG: 11,
      paddingInlineLG: 14,
      activeBorderColor: '#007aff',
      hoverBorderColor: 'rgba(0, 0, 0, 0.12)',
    },
    Button: {
      borderRadius: 12,
      controlHeight: 44,
      fontWeightStrong: 600,
    },
  },
}

export default function LoginPage() {
  const [form] = Form.useForm<{ login: string; password: string }>()
  const navigate = useNavigate()
  const login = Form.useWatch('login', form)
  const password = Form.useWatch('password', form)
  const mutation = useLoginMutation()

  const filled = Boolean(login?.trim()) && Boolean(password?.trim())

  const onFinish = (values: { login: string; password: string }) => {
    mutation.mutate(
      { login: values.login.trim(), password: values.password },
      {
        onSuccess: (data) => {
          localStorage.setItem(AUTH_TOKEN_KEY, data.token)
          message.success('Вход выполнен')
          navigate('/home', { replace: true })
        },
        onError: (err: Error) => {
          message.error(err.message)
        },
      },
    )
  }

  return (
    <div className={styles.page}>
      <ConfigProvider theme={loginTheme}>
        <div className={styles.container}>
          <Card className={styles.card} styles={{ body: { padding: 0 } }}>
            <div className={styles.inner}>
              <h1 className={styles.title}>Вход</h1>
              <p className={styles.subtitle}>Войдите, чтобы открыть панель</p>
              <Form
                className={styles.form}
                form={form}
                layout="vertical"
                requiredMark={false}
                onFinish={onFinish}
              >
                <Form.Item
                  label="Логин"
                  name="login"
                  rules={[{ required: true, message: 'Введите логин' }]}
                >
                  <Input autoComplete="username" size="large" placeholder="" />
                </Form.Item>
                <Form.Item
                  label="Пароль"
                  name="password"
                  rules={[{ required: true, message: 'Введите пароль' }]}
                >
                  <Input.Password
                    autoComplete="current-password"
                    size="large"
                    placeholder=""
                  />
                </Form.Item>
                <Form.Item style={{ marginBottom: 0 }}>
                  <div className={styles.actions}>
                    <Button
                      type="text"
                      className={styles.reset}
                      onClick={() => form.resetFields()}
                    >
                      Сбросить
                    </Button>
                    <Button
                      type="primary"
                      className={styles.submit}
                      htmlType="submit"
                      loading={mutation.isPending}
                      disabled={!filled}
                    >
                      Войти
                    </Button>
                  </div>
                </Form.Item>
              </Form>
            </div>
          </Card>
        </div>
      </ConfigProvider>
    </div>
  )
}
