'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Store, Users, ShieldCheck } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  username: string
  password: string
  role: 'superadmin' | 'admin' | 'empleado'
  storeType: 'ropa' | 'muebles' | 'cerveza' | null
  createdAt: string
  isBlocked: boolean
  name: string
}

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Inicializar datos de ejemplo si no existen
    const users = localStorage.getItem('users')
    if (!users) {
      const defaultUsers: User[] = [
        {
          id: '1',
          username: 'superadmin',
          password: 'admin123',
          role: 'superadmin',
          storeType: null,
          createdAt: new Date().toISOString(),
          isBlocked: false,
          name: 'Super Administrador'
        },
        {
          id: '2',
          username: 'tienda_ropa',
          password: 'ropa123',
          role: 'admin',
          storeType: 'ropa',
          createdAt: new Date().toISOString(),
          isBlocked: false,
          name: 'Admin Tienda Ropa'
        },
        {
          id: '3',
          username: 'tienda_muebles',
          password: 'muebles123',
          role: 'admin',
          storeType: 'muebles',
          createdAt: new Date().toISOString(),
          isBlocked: false,
          name: 'Admin Tienda Muebles'
        },
        {
          id: '4',
          username: 'agencia_cerveza',
          password: 'cerveza123',
          role: 'admin',
          storeType: 'cerveza',
          createdAt: new Date().toISOString(),
          isBlocked: false,
          name: 'Admin Agencia Cerveza'
        }
      ]
      localStorage.setItem('users', JSON.stringify(defaultUsers))
    }
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const users: User[] = JSON.parse(localStorage.getItem('users') || '[]')
      const user = users.find(u => u.username === username && u.password === password)

      if (!user) {
        setError('Usuario o contraseña incorrectos')
        return
      }

      // Verificar si la cuenta está bloqueada
      const accountAge = Date.now() - new Date(user.createdAt).getTime()
      const thirtyDaysInMs = 30 * 24 * 60 * 60 * 1000
      
      if (accountAge > thirtyDaysInMs && user.role !== 'superadmin') {
        // Bloquear cuenta automáticamente
        user.isBlocked = true
        const updatedUsers = users.map(u => u.id === user.id ? user : u)
        localStorage.setItem('users', JSON.stringify(updatedUsers))
      }

      if (user.isBlocked) {
        setError('Tu cuenta ha sido bloqueada. Contacta al administrador.')
        return
      }

      // Guardar sesión
      localStorage.setItem('currentUser', JSON.stringify(user))

      // Redirigir según el rol
      if (user.role === 'superadmin') {
        router.push('/superadmin')
      } else if (user.role === 'admin') {
        router.push(`/dashboard/${user.storeType}`)
      } else {
        router.push(`/empleado/${user.storeType}`)
      }
    } catch (error) {
      setError('Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <Store className="w-6 h-6 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold">Sistema de Contabilidad</CardTitle>
            <CardDescription>Ingresa tus credenciales para acceder</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Usuario</Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
              </Button>
            </form>
            
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Usuarios de prueba:</h3>
              <div className="text-sm space-y-1">
                <div><strong>Super Admin:</strong> superadmin / admin123</div>
                <div><strong>Tienda Ropa:</strong> tienda_ropa / ropa123</div>
                <div><strong>Tienda Muebles:</strong> tienda_muebles / muebles123</div>
                <div><strong>Agencia Cerveza:</strong> agencia_cerveza / cerveza123</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
