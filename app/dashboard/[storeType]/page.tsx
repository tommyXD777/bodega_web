'use client'

import { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Package, ShoppingCart, Users, FileText, Download, Plus, Edit, Trash2, LogOut, CreditCard, Calendar, X } from 'lucide-react'
import { useRouter, useParams } from 'next/navigation'

interface Product {
  id: string
  name: string
  priceProvider: number
  priceClient: number
  stock: number
  category: string
  storeType: string
}

type PaymentType = 'cash' | 'credit'
type BasketType = 'canasta' | 'canasta_mixta' | 'unidad'

interface Sale {
  id: string
  productId: string
  productName: string
  quantity: number // Always in units
  unitPrice: number
  total: number
  customerName: string
  customerPhone: string
  date: string
  employeeId: string
  storeType: string
  paymentType?: PaymentType
  basketType?: BasketType
  batchId?: string
}

interface Employee {
  id: string
  name: string
  username: string
  password: string
  storeType: string
  createdAt: string
}

interface Credit {
  id: string
  customerName: string
  customerPhone: string
  customerAddress: string
  productName: string
  totalAmount: number
  paidAmount: number
  remainingAmount: number
  installments: number
  installmentAmount: number
  nextPaymentDate: string
  status: 'active' | 'completed' | 'overdue'
  createdAt: string
  storeType: string
}

type BeerSaleMode = 'unidad' | 'canasta' | 'canasta_mixta'
const CANASTA_UNITS = 30

export default function DashboardPage() {
  const params = useParams()
  const router = useRouter()
  const storeType = params.storeType as string

  const [products, setProducts] = useState<Product[]>([])
  const [sales, setSales] = useState<Sale[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [credits, setCredits] = useState<Credit[]>([])
  const [currentUser, setCurrentUser] = useState<any>(null)

  // Estados para formularios
  const [showProductForm, setShowProductForm] = useState(false)
  const [showEmployeeForm, setShowEmployeeForm] = useState(false)
  const [showSaleForm, setShowSaleForm] = useState(false)
  const [showCreditForm, setShowCreditForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)

  const [productForm, setProductForm] = useState({
    name: '',
    priceProvider: '',
    priceClient: '',
    stock: '',
    category: ''
  })

  const [employeeForm, setEmployeeForm] = useState({
    name: '',
    username: '',
    password: ''
  })

  // Beer (cerveza) sale mode support
  type MixItem = { id: string; productId: string; quantity: string }
  const [saleForm, setSaleForm] = useState({
    productId: '',
    quantity: '',
    customerName: '',
    customerPhone: '',
    paymentType: 'cash' as PaymentType,
    // beer-specific
    saleMode: 'unidad' as BeerSaleMode,
    mixItems: [] as MixItem[],
  })

  const [creditForm, setCreditForm] = useState({
    customerName: '',
    customerPhone: '',
    customerAddress: '',
    productName: '',
    totalAmount: '',
    installments: '',
    firstPayment: ''
  })

  useEffect(() => {
    // Verificar autenticación
    const userData = localStorage.getItem('currentUser')
    if (!userData) {
      router.push('/')
      return
    }

    const user = JSON.parse(userData)
    if (user.role !== 'admin' || user.storeType !== storeType) {
      router.push('/')
      return
    }

    setCurrentUser(user)
    loadData()
  }, [router, storeType])

  const loadData = () => {
    // Cargar productos
    const productsData = localStorage.getItem('products')
    if (productsData) {
      const allProducts = JSON.parse(productsData)
      setProducts(allProducts.filter((p: Product) => p.storeType === storeType))
    }

    // Cargar ventas
    const salesData = localStorage.getItem('sales')
    if (salesData) {
      const allSales = JSON.parse(salesData)
      setSales(allSales.filter((s: Sale) => s.storeType === storeType))
    }

    // Cargar empleados
    const employeesData = localStorage.getItem('employees')
    if (employeesData) {
      const allEmployees = JSON.parse(employeesData)
      setEmployees(allEmployees.filter((e: Employee) => e.storeType === storeType))
    }

    // Cargar créditos (solo para muebles)
    if (storeType === 'muebles') {
      const creditsData = localStorage.getItem('credits')
      if (creditsData) {
        const allCredits = JSON.parse(creditsData)
        setCredits(allCredits.filter((c: Credit) => c.storeType === storeType))
      }
    }
  }

  const handleCreateProduct = (e: React.FormEvent) => {
    e.preventDefault()
    const newProduct: Product = {
      id: Date.now().toString(),
      name: productForm.name,
      priceProvider: parseFloat(productForm.priceProvider),
      priceClient: parseFloat(productForm.priceClient),
      stock: parseInt(productForm.stock),
      category: productForm.category,
      storeType
    }

    const allProducts = JSON.parse(localStorage.getItem('products') || '[]')
    const updatedProducts = [...allProducts, newProduct]
    localStorage.setItem('products', JSON.stringify(updatedProducts))
    
    setProducts([...products, newProduct])
    setShowProductForm(false)
    setProductForm({ name: '', priceProvider: '', priceClient: '', stock: '', category: '' })
  }

  const handleCreateEmployee = (e: React.FormEvent) => {
    e.preventDefault()
    const newEmployee: Employee = {
      id: Date.now().toString(),
      name: employeeForm.name,
      username: employeeForm.username,
      password: employeeForm.password,
      storeType,
      createdAt: new Date().toISOString()
    }

    // Agregar también a usuarios
    const users = JSON.parse(localStorage.getItem('users') || '[]')
    const newUser = {
      id: newEmployee.id,
      username: newEmployee.username,
      password: newEmployee.password,
      role: 'empleado',
      storeType,
      createdAt: new Date().toISOString(),
      isBlocked: false,
      name: newEmployee.name
    }
    users.push(newUser)
    localStorage.setItem('users', JSON.stringify(users))

    const allEmployees = JSON.parse(localStorage.getItem('employees') || '[]')
    const updatedEmployees = [...allEmployees, newEmployee]
    localStorage.setItem('employees', JSON.stringify(updatedEmployees))
    
    setEmployees([...employees, newEmployee])
    setShowEmployeeForm(false)
    setEmployeeForm({ name: '', username: '', password: '' })
  }

  // Helpers for cerveza sale form
  const beerSelectedProduct = useMemo(() => {
    return products.find(p => p.id === saleForm.productId) || null
  }, [products, saleForm.productId])

  const mixTotals = useMemo(() => {
    // Compute totals for canasta mixta
    let totalUnits = 0
    let totalCost = 0
    for (const item of saleForm.mixItems) {
      const prod = products.find(p => p.id === item.productId)
      const units = parseInt(item.quantity || '0') || 0
      if (!prod || units <= 0) continue
      totalUnits += units
      totalCost += units * prod.priceClient
    }
    const canastas = totalUnits / CANASTA_UNITS
    const isValidMultiple = totalUnits > 0 && totalUnits % CANASTA_UNITS === 0
    return { totalUnits, totalCost, canastas, isValidMultiple }
  }, [saleForm.mixItems, products])

  const handleSale = (e: React.FormEvent) => {
    e.preventDefault()

    if (storeType === 'cerveza') {
      // Beer sale modes
      if (saleForm.saleMode === 'unidad') {
        const product = products.find(p => p.id === saleForm.productId)
        if (!product || product.stock < parseInt(saleForm.quantity)) {
          alert('Producto no disponible o stock insuficiente')
          return
        }
        const quantityUnits = parseInt(saleForm.quantity)
        const total = product.priceClient * quantityUnits

        const newSale: Sale = {
          id: Date.now().toString(),
          productId: product.id,
          productName: product.name,
          quantity: quantityUnits,
          unitPrice: product.priceClient,
          total,
          customerName: saleForm.customerName,
          customerPhone: saleForm.customerPhone,
          date: new Date().toISOString(),
          employeeId: currentUser.id,
          storeType,
          paymentType: 'cash',
          basketType: 'unidad',
        }

        // Update stocks
        applyStockDeduction([{ productId: product.id, units: quantityUnits }])

        persistSaleRecords([newSale])
        resetSaleForm()
        return
      }

      if (saleForm.saleMode === 'canasta') {
        const product = products.find(p => p.id === saleForm.productId)
        const canastas = parseInt(saleForm.quantity)
        if (!product || !canastas || canastas <= 0) {
          alert('Selecciona un producto y una cantidad válida de canastas')
          return
        }
        const requiredUnits = canastas * CANASTA_UNITS
        if (product.stock < requiredUnits) {
          alert(`Stock insuficiente. Requiere ${requiredUnits} unidades (30 por canasta).`)
          return
        }

        const total = product.priceClient * requiredUnits

        const newSale: Sale = {
          id: Date.now().toString(),
          productId: product.id,
          productName: product.name,
          quantity: requiredUnits, // units
          unitPrice: product.priceClient,
          total,
          customerName: saleForm.customerName,
          customerPhone: saleForm.customerPhone,
          date: new Date().toISOString(),
          employeeId: currentUser.id,
          storeType,
          paymentType: 'cash',
          basketType: 'canasta',
        }

        applyStockDeduction([{ productId: product.id, units: requiredUnits }])
        persistSaleRecords([newSale])
        resetSaleForm()
        return
      }

      if (saleForm.saleMode === 'canasta_mixta') {
        if (!saleForm.mixItems.length) {
          alert('Agrega al menos un producto a la canasta mixta')
          return
        }

        // Validate totals are multiple of 30
        if (!mixTotals.isValidMultiple) {
          alert('El total de unidades en la canasta mixta debe ser múltiplo de 30')
          return
        }

        // Validate stocks per item
        for (const item of saleForm.mixItems) {
          const units = parseInt(item.quantity || '0') || 0
          if (units <= 0) {
            alert('Todas las cantidades deben ser mayores que 0')
            return
          }
          const product = products.find(p => p.id === item.productId)
          if (!product) {
            alert('Producto inválido en canasta mixta')
            return
          }
          if (product.stock < units) {
            alert(`Stock insuficiente para ${product.name}. Necesitas ${units} unidades.`)
            return
          }
        }

        const batchId = `${Date.now()}-mix`
        const newSales: Sale[] = saleForm.mixItems.map(item => {
          const prod = products.find(p => p.id === item.productId)!
          const units = parseInt(item.quantity)
          return {
            id: `${Date.now()}-${prod.id}-${Math.random().toString(36).slice(2,8)}`,
            productId: prod.id,
            productName: prod.name,
            quantity: units,
            unitPrice: prod.priceClient,
            total: prod.priceClient * units,
            customerName: saleForm.customerName,
            customerPhone: saleForm.customerPhone,
            date: new Date().toISOString(),
            employeeId: currentUser.id,
            storeType,
            paymentType: 'cash',
            basketType: 'canasta_mixta',
            batchId,
          }
        })

        const deductions = saleForm.mixItems.map(item => ({
          productId: item.productId,
          units: parseInt(item.quantity)
        }))

        applyStockDeduction(deductions)
        persistSaleRecords(newSales)
        resetSaleForm()
        return
      }

      // Fallback (should not happen)
      alert('Modo de venta no válido')
      return
    }

    // Resto de tiendas (ropa, muebles) usan flujo estándar previo
    const product = products.find(p => p.id === saleForm.productId)
    if (!product || product.stock < parseInt(saleForm.quantity)) {
      alert('Producto no disponible o stock insuficiente')
      return
    }

    const quantity = parseInt(saleForm.quantity)
    const total = product.priceClient * quantity

    const newSale: Sale = {
      id: Date.now().toString(),
      productId: product.id,
      productName: product.name,
      quantity,
      unitPrice: product.priceClient,
      total,
      customerName: saleForm.customerName,
      customerPhone: saleForm.customerPhone,
      date: new Date().toISOString(),
      employeeId: currentUser.id,
      storeType,
      paymentType: saleForm.paymentType
    }

    // Actualizar stock
    const updatedProducts = products.map(p => 
      p.id === product.id ? { ...p, stock: p.stock - quantity } : p
    )
    setProducts(updatedProducts)

    const allProducts = JSON.parse(localStorage.getItem('products') || '[]')
    const updatedAllProducts = allProducts.map((p: Product) => 
      p.id === product.id ? { ...p, stock: p.stock - quantity } : p
    )
    localStorage.setItem('products', JSON.stringify(updatedAllProducts))

    // Guardar venta
    const allSales = JSON.parse(localStorage.getItem('sales') || '[]')
    const updatedSales = [...allSales, newSale]
    localStorage.setItem('sales', JSON.stringify(updatedSales))
    setSales([...sales, newSale])

    // Si es a crédito y es tienda de muebles, crear registro de crédito
    if (saleForm.paymentType === 'credit' && storeType === 'muebles') {
      const installmentAmount = total / 12 // 12 cuotas por defecto
      const newCredit: Credit = {
        id: Date.now().toString(),
        customerName: saleForm.customerName,
        customerPhone: saleForm.customerPhone,
        customerAddress: '',
        productName: product.name,
        totalAmount: total,
        paidAmount: 0,
        remainingAmount: total,
        installments: 12,
        installmentAmount,
        nextPaymentDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active',
        createdAt: new Date().toISOString(),
        storeType
      }

      const allCredits = JSON.parse(localStorage.getItem('credits') || '[]')
      const updatedCredits = [...allCredits, newCredit]
      localStorage.setItem('credits', JSON.stringify(updatedCredits))
      setCredits([...credits, newCredit])
    }

    setShowSaleForm(false)
    setSaleForm({ productId: '', quantity: '', customerName: '', customerPhone: '', paymentType: 'cash', saleMode: 'unidad', mixItems: [] })
  }

  function applyStockDeduction(deductions: { productId: string; units: number }[]) {
    // Update in-memory
    const updatedProducts = products.map(p => {
      const d = deductions.find(dd => dd.productId === p.id)
      if (!d) return p
      return { ...p, stock: p.stock - d.units }
    })
    setProducts(updatedProducts)

    // Update localStorage
    const allProducts = JSON.parse(localStorage.getItem('products') || '[]') as Product[]
    const updatedAllProducts = allProducts.map((p: Product) => {
      const d = deductions.find(dd => dd.productId === p.id)
      if (!d) return p
      return { ...p, stock: p.stock - d.units }
    })
    localStorage.setItem('products', JSON.stringify(updatedAllProducts))
  }

  function persistSaleRecords(newSales: Sale[]) {
    const allSales = JSON.parse(localStorage.getItem('sales') || '[]')
    const updatedSales = [...allSales, ...newSales]
    localStorage.setItem('sales', JSON.stringify(updatedSales))
    setSales(prev => [...prev, ...newSales])

    setShowSaleForm(false)
  }

  function resetSaleForm() {
    setSaleForm({
      productId: '',
      quantity: '',
      customerName: '',
      customerPhone: '',
      paymentType: 'cash',
      saleMode: 'unidad',
      mixItems: [],
    })
  }

  const generateTicket = (sale: Sale) => {
    const ticketContent = `
TICKET DE VENTA
================
Tienda: ${storeType.toUpperCase()}
Fecha: ${new Date(sale.date).toLocaleString()}
Empleado: ${currentUser.name}

${sale.basketType === 'canasta' ? 'TIPO: CANASTA (30 u/canasta)' : sale.basketType === 'canasta_mixta' ? 'TIPO: CANASTA MIXTA' : ''}

PRODUCTO: ${sale.productName}
Cantidad (unidades): ${sale.quantity}
Precio Unit: $${sale.unitPrice}
TOTAL: $${sale.total}

Cliente: ${sale.customerName}
Teléfono: ${sale.customerPhone}

¡Gracias por su compra!
================
    `
    
    const blob = new Blob([ticketContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ticket-${sale.id}.txt`
    a.click()
  }

  const exportToExcel = () => {
    const csvContent = [
      ['Fecha', 'Producto', 'Cantidad (u)', 'Precio Unit.', 'Total', 'Cliente', 'Empleado', 'Tipo Canasta'],
      ...sales.map(sale => [
        new Date(sale.date).toLocaleDateString(),
        sale.productName,
        sale.quantity,
        sale.unitPrice,
        sale.total,
        sale.customerName,
        currentUser.name,
        sale.basketType ? sale.basketType : ''
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ventas-${storeType}-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  const handleLogout = () => {
    localStorage.removeItem('currentUser')
    router.push('/')
  }

  const getStoreTitle = () => {
    switch (storeType) {
      case 'ropa': return 'Tienda de Ropa'
      case 'muebles': return 'Tienda de Muebles'
      case 'cerveza': return 'Agencia de Cerveza'
      default: return 'Tienda'
    }
  }

  if (!currentUser) return <div>Cargando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <Package className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold">{getStoreTitle()}</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Bienvenido, {currentUser.name}</span>
            <Button onClick={handleLogout} variant="outline">
              <LogOut className="w-4 h-4 mr-2" />
              Cerrar Sesión
            </Button>
          </div>
        </div>

        <Tabs defaultValue="products" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="products">Productos</TabsTrigger>
            <TabsTrigger value="sales">Ventas</TabsTrigger>
            <TabsTrigger value="employees">Empleados</TabsTrigger>
            {storeType === 'muebles' && <TabsTrigger value="credits">Créditos</TabsTrigger>}
            <TabsTrigger value="reports">Reportes</TabsTrigger>
          </TabsList>

          <TabsContent value="products">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Gestión de Productos</CardTitle>
                    <CardDescription>Administra el inventario de tu tienda</CardDescription>
                  </div>
                  <Button onClick={() => setShowProductForm(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Producto
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {products.map(product => (
                    <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-semibold">{product.name}</h3>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>Precio Proveedor: ${product.priceProvider}</span>
                          <span>Precio Cliente: ${product.priceClient}</span>
                          <span>Stock: {product.stock}</span>
                          <span>Categoría: {product.category}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sales">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Registro de Ventas</CardTitle>
                    <CardDescription>Historial de todas las ventas realizadas</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={() => setShowSaleForm(true)}>
                      <ShoppingCart className="w-4 h-4 mr-2" />
                      Nueva Venta
                    </Button>
                    <Button onClick={exportToExcel} variant="outline">
                      <Download className="w-4 h-4 mr-2" />
                      Exportar Excel
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sales.map(sale => (
                    <div key={sale.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 flex-wrap">
                          <h3 className="font-semibold">{sale.productName}</h3>
                          {/* Payment badge (credit only in muebles) */}
                          {sale.paymentType && (
                            <Badge>{sale.paymentType === 'cash' ? 'Contado' : 'Crédito'}</Badge>
                          )}
                          {/* Basket type badge */}
                          {sale.basketType && (
                            <Badge variant="secondary">
                              {sale.basketType === 'canasta'
                                ? 'Canasta'
                                : sale.basketType === 'canasta_mixta'
                                ? 'Canasta Mixta'
                                : 'Unidad'}
                            </Badge>
                          )}
                        </div>
                        <div className="flex gap-4 text-sm text-gray-600 flex-wrap">
                          <span>Cantidad (u): {sale.quantity}</span>
                          <span>Total: ${sale.total}</span>
                          <span>Cliente: {sale.customerName}</span>
                          <span>Fecha: {new Date(sale.date).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <Button size="sm" onClick={() => generateTicket(sale)}>
                        <FileText className="w-4 h-4 mr-2" />
                        Ticket
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="employees">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Gestión de Empleados</CardTitle>
                    <CardDescription>Administra el personal de tu tienda</CardDescription>
                  </div>
                  <Button onClick={() => setShowEmployeeForm(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Empleado
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {employees.map(employee => (
                    <div key={employee.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-semibold">{employee.name}</h3>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>Usuario: {employee.username}</span>
                          <span>Creado: {new Date(employee.createdAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {storeType === 'muebles' && (
            <TabsContent value="credits">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>Gestión de Créditos</CardTitle>
                      <CardDescription>Control de ventas a crédito y pagos</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {credits.map(credit => (
                      <div key={credit.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold">{credit.customerName}</h3>
                          <Badge variant={credit.status === 'active' ? 'default' : credit.status === 'completed' ? 'secondary' : 'destructive'}>
                            {credit.status === 'active' ? 'Activo' : credit.status === 'completed' ? 'Completado' : 'Vencido'}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p><strong>Producto:</strong> {credit.productName}</p>
                            <p><strong>Total:</strong> ${credit.totalAmount}</p>
                            <p><strong>Pagado:</strong> ${credit.paidAmount}</p>
                          </div>
                          <div>
                            <p><strong>Restante:</strong> ${credit.remainingAmount}</p>
                            <p><strong>Cuota:</strong> ${credit.installmentAmount}</p>
                            <p><strong>Próximo pago:</strong> {new Date(credit.nextPaymentDate).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <div className="flex gap-2 mt-3">
                          <Button size="sm">
                            <CreditCard className="w-4 h-4 mr-2" />
                            Registrar Pago
                          </Button>
                          <Button size="sm" variant="outline">
                            <Calendar className="w-4 h-4 mr-2" />
                            Ver Historial
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          )}

          <TabsContent value="reports">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Resumen de Ventas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {sales.length}
                      </div>
                      <div className="text-sm text-gray-600">Total Ventas</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        ${sales.reduce((sum, sale) => sum + sale.total, 0)}
                      </div>
                      <div className="text-sm text-gray-600">Ingresos Totales</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {products.reduce((sum, product) => sum + product.stock, 0)}
                      </div>
                      <div className="text-sm text-gray-600">Productos en Stock</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Modal Agregar Producto */}
        {showProductForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Agregar Producto</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateProduct} className="space-y-4">
                  <div>
                    <Label htmlFor="product-name">Nombre del Producto</Label>
                    <Input
                      id="product-name"
                      value={productForm.name}
                      onChange={(e) => setProductForm({...productForm, name: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="price-provider">Precio Proveedor</Label>
                    <Input
                      id="price-provider"
                      type="number"
                      step="0.01"
                      value={productForm.priceProvider}
                      onChange={(e) => setProductForm({...productForm, priceProvider: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="price-client">Precio Cliente</Label>
                    <Input
                      id="price-client"
                      type="number"
                      step="0.01"
                      value={productForm.priceClient}
                      onChange={(e) => setProductForm({...productForm, priceClient: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="stock">Stock Inicial</Label>
                    <Input
                      id="stock"
                      type="number"
                      value={productForm.stock}
                      onChange={(e) => setProductForm({...productForm, stock: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Categoría</Label>
                    <Input
                      id="category"
                      value={productForm.category}
                      onChange={(e) => setProductForm({...productForm, category: e.target.value})}
                      required
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="flex-1">Agregar</Button>
                    <Button type="button" variant="outline" onClick={() => setShowProductForm(false)}>
                      Cancelar
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal Agregar Empleado */}
        {showEmployeeForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Agregar Empleado</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateEmployee} className="space-y-4">
                  <div>
                    <Label htmlFor="employee-name">Nombre Completo</Label>
                    <Input
                      id="employee-name"
                      value={employeeForm.name}
                      onChange={(e) => setEmployeeForm({...employeeForm, name: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="employee-username">Usuario</Label>
                    <Input
                      id="employee-username"
                      value={employeeForm.username}
                      onChange={(e) => setEmployeeForm({...employeeForm, username: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="employee-password">Contraseña</Label>
                    <Input
                      id="employee-password"
                      type="password"
                      value={employeeForm.password}
                      onChange={(e) => setEmployeeForm({...employeeForm, password: e.target.value})}
                      required
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="flex-1">Agregar</Button>
                    <Button type="button" variant="outline" onClick={() => setShowEmployeeForm(false)}>
                      Cancelar
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal Nueva Venta */}
        {showSaleForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Nueva Venta</CardTitle>
                <CardDescription>
                  {storeType === 'cerveza'
                    ? 'En cerveza puedes vender por unidad, canasta (30 u) o canasta mixta.'
                    : storeType === 'muebles'
                      ? 'Puedes vender al contado o a crédito.'
                      : 'Venta estándar por unidades.'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSale} className="space-y-4">
                  {/* Cerveza: selector de tipo */}
                  {storeType === 'cerveza' && (
                    <div>
                      <Label>Tipo de Venta</Label>
                      <Select
                        value={saleForm.saleMode}
                        onValueChange={(value: BeerSaleMode) => setSaleForm(prev => ({ ...prev, saleMode: value }))}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Seleccionar tipo" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="unidad">Unidad</SelectItem>
                          <SelectItem value="canasta">Canasta (30 u)</SelectItem>
                          <SelectItem value="canasta_mixta">Canasta Mixta (30 u)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {/* Producto y cantidad para unidad/canasta */}
                  {(storeType !== 'cerveza' || saleForm.saleMode === 'unidad' || saleForm.saleMode === 'canasta') && (
                    <>
                      <div>
                        <Label htmlFor="sale-product">Producto</Label>
                        <Select
                          value={saleForm.productId}
                          onValueChange={(value) => setSaleForm({ ...saleForm, productId: value })}
                        >
                          <SelectTrigger id="sale-product">
                            <SelectValue placeholder="Seleccionar producto" />
                          </SelectTrigger>
                          <SelectContent>
                            {products.filter(p => p.stock > 0).map(product => (
                              <SelectItem key={product.id} value={product.id}>
                                {product.name} - ${product.priceClient} (Stock: {product.stock})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="sale-quantity">
                          {storeType === 'cerveza' && saleForm.saleMode === 'canasta' ? 'Cantidad de Canastas' : 'Cantidad (unidades)'}
                        </Label>
                        <Input
                          id="sale-quantity"
                          type="number"
                          min="1"
                          value={saleForm.quantity}
                          onChange={(e) => setSaleForm({ ...saleForm, quantity: e.target.value })}
                          required
                        />
                        {/* Preview for canasta */}
                        {storeType === 'cerveza' && saleForm.saleMode === 'canasta' && beerSelectedProduct && saleForm.quantity && parseInt(saleForm.quantity) > 0 && (
                          <div className="text-xs text-gray-600 mt-1">
                            Unidades totales: {parseInt(saleForm.quantity) * CANASTA_UNITS} • Total: ${ (parseInt(saleForm.quantity) * CANASTA_UNITS * beerSelectedProduct.priceClient).toFixed(2) }
                          </div>
                        )}
                      </div>
                    </>
                  )}

                  {/* Canasta Mixta builder */}
                  {storeType === 'cerveza' && saleForm.saleMode === 'canasta_mixta' && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label>Productos de la Canasta Mixta</Label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            setSaleForm(prev => ({
                              ...prev,
                              mixItems: [
                                ...prev.mixItems,
                                { id: Math.random().toString(36).slice(2, 9), productId: '', quantity: '' },
                              ],
                            }))
                          }
                        >
                          <Plus className="w-4 h-4 mr-1" /> Agregar
                        </Button>
                      </div>

                      {saleForm.mixItems.length === 0 && (
                        <p className="text-xs text-gray-500">Añade productos para armar la canasta mixta (30 unidades por canasta).</p>
                      )}

                      <div className="space-y-2">
                        {saleForm.mixItems.map((item, idx) => {
                          const p = products.find(pp => pp.id === item.productId)
                          const units = parseInt(item.quantity || '0') || 0
                          const rowTotal = p ? (p.priceClient * units) : 0
                          return (
                            <div key={item.id} className="grid grid-cols-12 gap-2 items-end">
                              <div className="col-span-7">
                                <Label className="text-xs">Producto</Label>
                                <Select
                                  value={item.productId}
                                  onValueChange={(value) => {
                                    setSaleForm(prev => ({
                                      ...prev,
                                      mixItems: prev.mixItems.map(mi => mi.id === item.id ? { ...mi, productId: value } : mi)
                                    }))
                                  }}
                                >
                                  <SelectTrigger>
                                    <SelectValue placeholder="Seleccionar producto" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {products.filter(p => p.stock > 0).map(product => (
                                      <SelectItem key={product.id} value={product.id}>
                                        {product.name} - ${product.priceClient} (S: {product.stock})
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="col-span-3">
                                <Label htmlFor={`mix-q-${idx}`} className="text-xs">Unidades</Label>
                                <Input
                                  id={`mix-q-${idx}`}
                                  type="number"
                                  min={1}
                                  value={item.quantity}
                                  onChange={(e) => {
                                    setSaleForm(prev => ({
                                      ...prev,
                                      mixItems: prev.mixItems.map(mi => mi.id === item.id ? { ...mi, quantity: e.target.value } : mi)
                                    }))
                                  }}
                                />
                              </div>
                              <div className="col-span-1 text-right text-xs text-gray-600">
                                {rowTotal > 0 ? `$${rowTotal.toFixed(0)}` : ''}
                              </div>
                              <div className="col-span-1 flex justify-end">
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => {
                                    setSaleForm(prev => ({
                                      ...prev,
                                      mixItems: prev.mixItems.filter(mi => mi.id !== item.id)
                                    }))
                                  }}
                                  aria-label="Quitar"
                                >
                                  <X className="w-4 h-4" />
                                </Button>
                              </div>
                              {p && units > p.stock && (
                                <div className="col-span-12 text-xs text-red-600 -mt-1">Stock insuficiente para {p.name}. Disponible: {p.stock}</div>
                              )}
                            </div>
                          )
                        })}
                      </div>

                      <div className="rounded-md border p-2 text-sm">
                        <div className="flex justify-between">
                          <span>Unidades totales</span>
                          <span>{mixTotals.totalUnits}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Canastas</span>
                          <span>{mixTotals.totalUnits > 0 ? (mixTotals.totalUnits / CANASTA_UNITS).toFixed(2) : '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total</span>
                          <span>${mixTotals.totalCost.toFixed(2)}</span>
                        </div>
                        {!mixTotals.isValidMultiple && mixTotals.totalUnits > 0 && (
                          <div className="text-xs text-amber-600 mt-1">
                            El total de unidades debe ser múltiplo de 30 (30 u por canasta).
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div>
                    <Label htmlFor="customer-name">Nombre del Cliente</Label>
                    <Input
                      id="customer-name"
                      value={saleForm.customerName}
                      onChange={(e) => setSaleForm({...saleForm, customerName: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="customer-phone">Teléfono del Cliente</Label>
                    <Input
                      id="customer-phone"
                      value={saleForm.customerPhone}
                      onChange={(e) => setSaleForm({...saleForm, customerPhone: e.target.value})}
                      required
                    />
                  </div>

                  {/* Tipo de pago solo para muebles */}
                  {storeType === 'muebles' && (
                    <div>
                      <Label htmlFor="payment-type">Tipo de Pago</Label>
                      <Select
                        value={saleForm.paymentType}
                        onValueChange={(value: PaymentType) => setSaleForm({ ...saleForm, paymentType: value })}
                      >
                        <SelectTrigger id="payment-type">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="cash">Contado</SelectItem>
                          <SelectItem value="credit">Crédito</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      className="flex-1"
                      disabled={
                        storeType === 'cerveza' &&
                        saleForm.saleMode === 'canasta_mixta' &&
                        (!mixTotals.isValidMultiple || mixTotals.totalUnits === 0)
                      }
                    >
                      Vender
                    </Button>
                    <Button type="button" variant="outline" onClick={() => { setShowSaleForm(false); resetSaleForm() }}>
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
</merged_code>
