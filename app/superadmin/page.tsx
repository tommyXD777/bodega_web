'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Users, Plus, Edit, Lock, Unlock, LogOut } from 'lucide-react'
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

export default function SuperAdminPage() {
  const [users, setUsers] = useState<User[]>([])
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    name: '',
    role: 'admin' as 'admin' | 'empleado',
    storeType: 'ropa' as 'ropa' | 'muebles' | 'cerveza'
  })
  const router = useRouter()

  useEffect(() => {
    // Verificar autenticación
    const currentUser = localStorage.getItem('currentUser')
    if (!currentUser) {
      router.push('/')
      return
    }

    const user = JSON.parse(currentUser)
    if (user.role !== 'superadmin') {
      router.push('/')
      return
    }

    loadUsers()
  }, [router])

  const loadUsers = () => {
    const usersData = localStorage.getItem('users')
    if (usersData) {
      setUsers(JSON.parse(usersData))
    }
  }

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault()
    const newUser: User = {
      id: Date.now().toString(),
      username: formData.username,
      password: formData.password,
      name: formData.name,
      role: formData.role,
      storeType: formData.storeType,
      createdAt: new Date().toISOString(),
      isBlocked: false
    }

    const updatedUsers = [...users, newUser]
    setUsers(updatedUsers)
    localStorage.setItem('users', JSON.stringify(updatedUsers))
    
    setShowCreateForm(false)
    setFormData({
      username: '',
      password: '',
      name: '',
      role: 'admin',
      storeType: 'ropa'
    })
  }

  const handleEditUser = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return

    const updatedUser = {
      ...editingUser,
      username: formData.username,
      password: formData.password,
      name: formData.name,
      role: formData.role,
      storeType: formData.storeType
    }

    const updatedUsers = users.map(u => u.id === editingUser.id ? updatedUser : u)
    setUsers(updatedUsers)
    localStorage.setItem('users', JSON.stringify(updatedUsers))
    
    setEditingUser(null)
    setFormData({
      username: '',
      password: '',
      name: '',
      role: 'admin',
      storeType: 'ropa'
    })
  }

  const toggleUserBlock = (userId: string) => {
    const updatedUsers = users.map(u => 
      u.id === userId ? { ...u, isBlocked: !u.isBlocked } : u
    )
    setUsers(updatedUsers)
    localStorage.setItem('users', JSON.stringify(updatedUsers))
  }

  const startEdit = (user: User) => {
    setEditingUser(user)
    setFormData({
      username: user.username,
      password: user.password,
      name: user.name,
      role: user.role as 'admin' | 'empleado',
      storeType: user.storeType || 'ropa'
    })
  }

  const handleLogout = () => {
    localStorage.removeItem('currentUser')
    router.push('/')
  }

  const getAccountStatus = (user: User) => {
    const accountAge = Date.now() - new Date(user.createdAt).getTime()
    const thirtyDaysInMs = 30 * 24 * 60 * 60 * 1000
    
    if (user.isBlocked) return 'Bloqueada'
    if (accountAge > thirtyDaysInMs && user.role !== 'superadmin') return 'Expirada'
    return 'Activa'
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold">Panel Super Administrador</h1>
          </div>
          <Button onClick={handleLogout} variant="outline">
            <LogOut className="w-4 h-4 mr-2" />
            Cerrar Sesión
          </Button>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Gestión de Usuarios</CardTitle>
                  <CardDescription>Administra las cuentas del sistema</CardDescription>
                </div>
                <Button onClick={() => setShowCreateForm(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Crear Usuario
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.filter(u => u.role !== 'superadmin').map(user => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold">{user.name}</h3>
                        <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                          {user.role === 'admin' ? 'Administrador' : 'Empleado'}
                        </Badge>
                        <Badge variant="outline">
                          {user.storeType === 'ropa' ? 'Tienda Ropa' : 
                           user.storeType === 'muebles' ? 'Tienda Muebles' : 'Agencia Cerveza'}
                        </Badge>
                        <Badge variant={getAccountStatus(user) === 'Activa' ? 'default' : 'destructive'}>
                          {getAccountStatus(user)}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">Usuario: {user.username}</p>
                      <p className="text-sm text-gray-500">
                        Creado: {new Date(user.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => startEdit(user)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant={user.isBlocked ? "default" : "destructive"}
                        onClick={() => toggleUserBlock(user.id)}
                      >
                        {user.isBlocked ? <Unlock className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Modal Crear Usuario */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Crear Nuevo Usuario</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateUser} className="space-y-4">
                  <div>
                    <Label htmlFor="name">Nombre Completo</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="username">Usuario</Label>
                    <Input
                      id="username"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="password">Contraseña</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="role">Rol</Label>
                    <Select value={formData.role} onValueChange={(value: 'admin' | 'empleado') => setFormData({...formData, role: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="admin">Administrador</SelectItem>
                        <SelectItem value="empleado">Empleado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="storeType">Tipo de Tienda</Label>
                    <Select value={formData.storeType} onValueChange={(value: 'ropa' | 'muebles' | 'cerveza') => setFormData({...formData, storeType: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ropa">Tienda de Ropa</SelectItem>
                        <SelectItem value="muebles">Tienda de Muebles</SelectItem>
                        <SelectItem value="cerveza">Agencia de Cerveza</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="flex-1">Crear</Button>
                    <Button type="button" variant="outline" onClick={() => setShowCreateForm(false)}>
                      Cancelar
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal Editar Usuario */}
        {editingUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Editar Usuario</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleEditUser} className="space-y-4">
                  <div>
                    <Label htmlFor="edit-name">Nombre Completo</Label>
                    <Input
                      id="edit-name"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-username">Usuario</Label>
                    <Input
                      id="edit-username"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-password">Contraseña</Label>
                    <Input
                      id="edit-password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-role">Rol</Label>
                    <Select value={formData.role} onValueChange={(value: 'admin' | 'empleado') => setFormData({...formData, role: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="admin">Administrador</SelectItem>
                        <SelectItem value="empleado">Empleado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="edit-storeType">Tipo de Tienda</Label>
                    <Select value={formData.storeType} onValueChange={(value: 'ropa' | 'muebles' | 'cerveza') => setFormData({...formData, storeType: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ropa">Tienda de Ropa</SelectItem>
                        <SelectItem value="muebles">Tienda de Muebles</SelectItem>
                        <SelectItem value="cerveza">Agencia de Cerveza</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="flex-1">Guardar</Button>
                    <Button type="button" variant="outline" onClick={() => setEditingUser(null)}>
                      Cancelar
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
