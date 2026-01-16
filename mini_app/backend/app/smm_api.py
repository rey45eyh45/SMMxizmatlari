# -*- coding: utf-8 -*-
"""
SMM Panel API integratsiyasi
"""
import httpx
from typing import Dict, Any, Optional
from .config import SMM_API_KEY, SMM_API_URL, SMMMAIN_API_URL, SMMMAIN_API_KEY


class SMMPanel:
    """SMM Panel API"""
    
    def __init__(self, api_url: str, api_key: str, name: str):
        self.api_url = api_url
        self.api_key = api_key
        self.name = name
    
    async def _request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """API so'rov yuborish"""
        data['key'] = self.api_key
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, data=data)
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_balance(self) -> float:
        """Balansni olish"""
        result = await self._request({'action': 'balance'})
        if 'balance' in result:
            return float(result['balance'])
        return 0.0
    
    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """Buyurtma qo'shish"""
        return await self._request({
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        })
    
    async def get_order_status(self, order_id: int) -> Dict[str, Any]:
        """Buyurtma holatini olish"""
        return await self._request({
            'action': 'status',
            'order': order_id
        })
    
    async def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """Buyurtmani bekor qilish"""
        return await self._request({
            'action': 'cancel',
            'order': order_id
        })


class MultiPanel:
    """Multi-panel boshqaruvi"""
    
    def __init__(self):
        self.panels: Dict[str, SMMPanel] = {}
        
        if SMM_API_KEY:
            self.panels['peakerr'] = SMMPanel(SMM_API_URL, SMM_API_KEY, "Peakerr")
        
        if SMMMAIN_API_KEY:
            self.panels['smmmain'] = SMMPanel(SMMMAIN_API_URL, SMMMAIN_API_KEY, "SMMMain")
    
    def get_panel(self, name: str) -> Optional[SMMPanel]:
        """Panelni olish"""
        return self.panels.get(name.lower())
    
    async def get_all_balances(self) -> Dict[str, float]:
        """Barcha panellar balansini olish"""
        balances = {}
        for name, panel in self.panels.items():
            try:
                balances[name] = await panel.get_balance()
            except:
                balances[name] = 0.0
        return balances
    
    async def add_order(self, panel_name: str, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """Buyurtma qo'shish"""
        panel = self.get_panel(panel_name)
        if not panel:
            return {"error": "Panel topilmadi"}
        return await panel.add_order(service_id, link, quantity)
    
    async def get_order_status(self, panel_name: str, order_id: int) -> Dict[str, Any]:
        """Buyurtma holatini olish"""
        panel = self.get_panel(panel_name)
        if not panel:
            return {"error": "Panel topilmadi"}
        return await panel.get_order_status(order_id)


# Global instance
smm_api = MultiPanel()
