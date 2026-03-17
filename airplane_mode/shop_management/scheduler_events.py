import frappe
from frappe.utils import today

def send_rent_reminders():
    # Check if reminders are enabled in Shop Settings
    settings = frappe.get_single("Shop Settings")
    
    if not settings.enable_rent_reminders:
        return

    # Get all leased shops
    shops = frappe.get_all("Shop", 
        filters={"status": "Leased"}, 
        fields=["name", "shop_name", "monthly_rent", "tenant_details"]
    )

    for shop in shops:
        tenant = frappe.get_doc("Tenant", shop.tenant_details)
        
        if not tenant.email:
            continue
        frappe.sendmail(
            recipients=[tenant.email],
            subject=f"Rent Due Reminder — {shop.shop_name}",
            message=f"""
                <p>Dear {tenant.name1},</p>
                <p>This is a reminder that your monthly rent of <strong>{shop.monthly_rent}</strong> 
                is due for shop <strong>{shop.shop_name}</strong>.</p>
                <p>Please make the payment at your earliest convenience.</p>
                <br>
                <p>Regards,<br>Airport Management</p>
            """
        )