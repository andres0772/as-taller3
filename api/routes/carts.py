from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models.cart import Cart, CartItem
from models.product import Product

router = APIRouter()


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional["ProductResponse"]

    class Config:
        from_attributes = True


class ProductInCart(BaseModel):
    id: int
    name: str
    price: float
    image_url: Optional[str]

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductInCart]

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]

    class Config:
        from_attributes = True


class AddItemRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class UpdateItemRequest(BaseModel):
    quantity: int


@router.get("/", response_model=CartResponse)
async def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        # Crear carrito si no existe
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Cargar los items con el producto
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

    return {"id": cart.id, "user_id": cart.user_id, "items": items}


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(item_data: AddItemRequest, db: Session = Depends(get_db)):
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente"
        )

    # Buscar o crear carrito
    cart = db.query(Cart).filter(Cart.user_id == item_data.user_id).first()
    if not cart:
        cart = Cart(user_id=item_data.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Verificar si el producto ya está en el carrito
    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id, CartItem.product_id == item_data.product_id
        )
        .first()
    )

    if existing_item:
        # Actualizar cantidad
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuficiente para la cantidad total",
            )
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Crear nuevo item
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int, item_data: UpdateItemRequest, db: Session = Depends(get_db)
):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado en el carrito",
        )

    # Verificar stock
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente"
        )

    item.quantity = item_data.quantity
    db.commit()
    db.refresh(item)

    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(item_id: int, db: Session = Depends(get_db)):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado en el carrito",
        )

    db.delete(item)
    db.commit()

    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        return None

    # Eliminar todos los items
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()

    return None
