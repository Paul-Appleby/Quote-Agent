const webhook_data = {
    "event": "sms_received",
    "contact": {
        "id": "abc123",
        "first_name": "Alex",
        "last_name": "Taylor",
        "email": "alex@example.com",
        "phone": "+15125551234"
    },
    "message": {
        "id": "msg789",
        "text": "Hey, I need info on scheduling a wax appointment.",
        "timestamp": "2025-06-10T15:23:45Z"
    },
    "metadata": {
        "source": "Twilio",
        "campaign": "summer-promo"
    }
}

const get_customer_info = (webhook_data) => {
    return `
    Name: {webhook_data['contact']['first_name']} {webhook_data['contact']['last_name']}
    Phone: {webhook_data['contact']['phone']}
    Email: {webhook_data['contact']['email']}
    Campaign: {webhook_data['metadata']['campaign']}
        `
}

const get_message = (webhook_data) => {
    return webhook_data['message']['text']
}

console.log(get_customer_info(webhook_data));
console.log(get_message(webhook_data));