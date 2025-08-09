'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ShoppingCart, FileText, LogOut, Package } from 'lucide-react'
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

interface Sale {
  id: string
  productId: string
  productName: string
  quantity: number
  unitPrice: number
  total: number
  customerName: string
  customerPhone: string
  date: string
  employeeId: string
  storeType: string
  paymentType?: 'cash' | 'credit'
}

export default function EmpleadoPage() {
  const params = useParams()
  const router = useRouter()
  const storeType = params.storeType as string

  const [products, setProducts] = useState<Product[]>([])
  const [sales, setSales] = useState<Sale[]>([])
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [showSaleForm, setShowSaleForm] = useState(false)

  const [saleForm, setSaleForm] = useState({
    productId: '',
    quantity: '',
    customerName: '',
    customerPhone: '',
    paymentType: 'cash' as 'cash' | 'credit'
  })

  useEffect(() => {
    // Verificar autenticación
    const userData = localStorage.getItem('currentUser')
    if (!userData) {
      router.push('/')
      return
    }

    const user = JSON.parse(userData)
    if (user.role !== 'empleado' || user.storeType !== storeType) {
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

    // Cargar ventas del empleado
    const salesData = localStorage.getItem('sales')
    if (salesData) {
      const allSales = JSON.parse(salesData)
      setSales(allSales.filter((s: Sale) => s.storeType === storeType))
    }
  }

  const handleSale = (e: React.FormEvent) => {
    e.preventDefault()
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

    setShowSaleForm(false)
    setSaleForm({ productId: '', quantity: '', customerName: '', customerPhone: '', paymentType: 'cash' })
  }

  const generateTicket = (sale: Sale) => {
    const ticketContent = `
TICKET DE VENTA
================
Tienda: ${storeType.toUpperCase()}
Fecha: ${new Date(sale.date).toLocaleString()}
Empleado: ${currentUser.name}

PRODUCTO: ${sale.productName}
Cantidad: ${sale.quantity}
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
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <Package className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold">{getStoreTitle()} - Empleado</h1>
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
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="products">Productos</TabsTrigger>
            <TabsTrigger value="sales">Ventas</TabsTrigger>
            <TabsTrigger value="new-sale">Nueva Venta</TabsTrigger>
          </TabsList>

          <TabsContent value="products">
            <Card>
              <CardHeader>
                <CardTitle>Productos Disponibles</CardTitle>
                <CardDescription>Consulta el inventario disponible</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {products.map(product => (
                    <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-semibold">{product.name}</h3>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>Precio: ${product.priceClient}</span>
                          <span>Stock: {product.stock}</span>
                          <span>Categoría: {product.category}</span>
                        </div>
                      </div>
                      <Badge variant={product.stock > 0 ? "default" : "destructive"}>
                        {product.stock > 0 ? "Disponible" : "Agotado"}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sales">
            <Card>
              <CardHeader>
                <CardTitle>Mis Ventas</CardTitle>
                <CardDescription>Historial de ventas realizadas</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sales.filter(sale => sale.employeeId === currentUser.id).map(sale => (
                    <div key={sale.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold">{sale.productName}</h3>
                          <Badge>{sale.paymentType === 'cash' ? 'Contado' : 'Crédito'}</Badge>
                        </div>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>Cantidad: {sale.quantity}</span>
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

          <TabsContent value="new-sale">
            <Card>
              <CardHeader>
                <CardTitle>Realizar Nueva Venta</CardTitle>
                <CardDescription>Procesa una venta de productos</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSale} className="space-y-4 max-w-md">
                  <div>
                    <Label htmlFor="sale-product">Producto</Label>
                    <Select value={saleForm.productId} onValueChange={(value) => setSaleForm({...saleForm, productId: value})}>
                      <SelectTrigger>
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
                    <Label htmlFor="sale-quantity">Cantidad</Label>
                    <Input
                      id="sale-quantity"
                      type="number"
                      min="1"
                      value={saleForm.quantity}
                      onChange={(e) => setSaleForm({...saleForm, quantity: e.target.value})}
                      required
                    />
                  </div>
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
                  {storeType === 'muebles' && (
                    <div>
                      <Label htmlFor="payment-type">Tipo de Pago</Label>
                      <Select value={saleForm.paymentType} onValueChange={(value: 'cash' | 'credit') => setSaleForm({...saleForm, paymentType: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="cash">Contado</SelectItem>
                          <SelectItem value="credit">Crédito</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  <Button type="submit" className="w-full">
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    Realizar Venta
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Resumen de ventas del día */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Resumen del Día</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {sales.filter(sale => 
                    sale.employeeId === currentUser.id && 
                    new Date(sale.date).toDateString() === new Date().toDateString()
                  ).length}
                </div>
                <div className="text-sm text-gray-600">Ventas Hoy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  ${sales.filter(sale => 
                    sale.employeeId === currentUser.id && 
                    new Date(sale.date).toDateString() === new Date().toDateString()
                  ).reduce((sum, sale) => sum + sale.total, 0)}
                </div>
                <div className="text-sm text-gray-600">Ingresos Hoy</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
