class M_Pesa_WhatsApp:

    def __init__(self, token: str, phone_number_id: str, mpesa_consumer_key: str, mpesa_consumer_secret: str):
        super().__init__(token, phone_number_id)
        self.mpesa_consumer_key = mpesa_consumer_key
        self.mpesa_consumer_secret = mpesa_consumer_secret