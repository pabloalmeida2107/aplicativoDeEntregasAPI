from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from dependecies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema
from models import Pedido,Usuario,ItemPedido

order_router = APIRouter(prefix="/order", tags=["order"],dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam de autenticação
    """
    return {"mensagem": " você está acessando a rota de pedidos"}

@order_router.post("/pedido")
async def cria_pedido(pedido_schema: PedidoSchema, Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario= pedido_schema.id)
    Session.add(novo_pedido)
    Session.commit()
    return{"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int,session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, details ="Você não tem autorização para fazer essa modifição")
    
    pedido.status = "CANCELADO"
    session.commit()

    return{

        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=400, details ="Você não tem autorização para fazer essa operação")
    else:
        pedidos = session.query(Pedido).all()
        return{
            "pedidos": pedidos
        } 

@order_router.post("/pedido/adicionar-item/{id_pedido}")   
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema,session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, details ="pedido não existente")
    
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, details ="Você não tem autorização para fazer essa operação")
    
    item_pedido = ItemPedido(item_pedido_schema.quantidade,item_pedido_schema.sabor,item_pedido_schema.tamanho,item_pedido_schema.preco_unitario,id_pedido)
    
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()

    return{
        "mensagem": "item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }


@order_router.delete("/pedido/remover-item/{id_item_pedido}")   
async def remover_item_pedido(id_item_pedido: int,session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id== id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, details ="Item no pedido não existente")
    
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, details ="Você não tem autorização para fazer essa operação")
    
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()

    return{
        "mensagem": "item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.put("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int,session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, details ="Você não tem autorização para fazer essa modifição")
    
    pedido.status = "FINALIZADO"
    session.commit()

    return{

        "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",
        "pedido": pedido
    }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int,session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, details ="Você não tem autorização para fazer essa modifição")
    
    return{

        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

