import { Button, Form, Input, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useLoginMutation } from '../hooks/useLoginMutation'
import { AUTH_TOKEN_KEY } from '../constants/auth'

export default function LoginPage() {
  const [form] = Form.useForm<{ login: string; password: string }>()
  const navigate = useNavigate()
  const login = Form.useWatch('login', form)
  const password = Form.useWatch('password', form)
  const mutation = useLoginMutation()

  const filled =
    Boolean(login?.trim()) && Boolean(password?.trim())

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
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
      }}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        style={{ width: 360, maxWidth: '100%' }}
      >
        <Form.Item
          label="Логин"
          name="login"
          rules={[{ required: true, message: 'Введите логин' }]}
        >
          <Input autoComplete="username" />
        </Form.Item>
        <Form.Item
          label="Пароль"
          name="password"
          rules={[{ required: true, message: 'Введите пароль' }]}
        >
          <Input.Password autoComplete="current-password" />
        </Form.Item>
        <Form.Item>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <Button onClick={() => form.resetFields()}>Сбросить</Button>
            <Button
              type="primary"
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
  )
}
