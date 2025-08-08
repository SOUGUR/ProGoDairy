from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
import json



def supplier_list(request):
    query = """
        query {
            suppliers {
                id
                phoneNumber
                email
                dailyCapacity
                totalDairyCows
                annualOutput
            }
        }
    """

    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()

        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")

        suppliers = json_data['data']['suppliers']
        return render(request, 'supplier_list.html', {'suppliers': suppliers})

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Request error: {e}")

    except ValueError as e:
        return HttpResponse(f"JSON decode error: {e}<br><br>Response text:<br>{response.text}")
    

def create_supplier(request):
    sessionid = request.COOKIES.get('sessionid')
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        daily_capacity = float(request.POST.get('daily_capacity'))
        total_dairy_cows = int(request.POST.get('total_dairy_cows'))
        annual_output = float(request.POST.get('annual_output'))
        distance_from_plant = float(request.POST.get('distance_from_plant'))
        aadhar_number = request.POST.get('aadhar_number')
        address = request.POST.get('address')
        bank_account_number = request.POST.get('bank_account_number')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')

        mutation = f"""
        mutation {{
            createSupplier(
                phoneNumber: "{phone_number}",
                email: "{email}",
                dailyCapacity: {daily_capacity},
                totalDairyCows: {total_dairy_cows},
                annualOutput: {annual_output},
                distanceFromPlant: {distance_from_plant},
                aadharNumber: "{aadhar_number}",
                address: "{address}",
                bankAccountNumber: "{bank_account_number}",
                bankName: "{bank_name}",
                ifscCode: "{ifsc_code}"
            ) {{
                id
                phoneNumber
                email
            }}
        }}
        """

        try:
            response = requests.post(
                'http://localhost:8000/graphql/',
                json={'query': mutation},
                headers={'Content-Type': 'application/json',
                        'Cookie': f'sessionid={sessionid}'
                        }
                
            )

            if response.status_code != 200:
                return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

            json_data = response.json()
            if 'errors' in json_data:
                return HttpResponse(f"GraphQL errors: {json_data['errors']}")
            
            messages.success(request, f"Supplier profile for user {email} created successfully")
            return redirect('supplier_list')  

        except requests.exceptions.RequestException as e:
            return HttpResponse(f"Request error: {e}")
    else:
        user = request.user
        query = """
            query {
                mySupplier {
                    id
                    phoneNumber
                    email
                    dailyCapacity
                    totalDairyCows
                    annualOutput
                    distanceFromPlant
                    bankAccountNumber
                }
            }
        """
        try:
            response = requests.post(
                'http://localhost:8000/graphql/',
                json={'query': query},
                headers={
                    'Content-Type': 'application/json',
                    'Cookie': f'sessionid={sessionid}',
                }
            )
            supplier_data = None
            if response.status_code == 200:
                json_data = response.json()
                if 'data' in json_data and 'mySupplier' in json_data['data']:
                    supplier_data = json_data['data']['mySupplier']

            return render(request, 'create_supplier.html', {
                'user': user,
                'supplier': supplier_data
            })
        except Exception as e:
            return render(request, 'create_supplier.html', {
                'user': user,
                'error': str(e)
            })

def milk_lot_result_list_view(request):
    query = """
        query {
            milkLotList {
                id
                volumeL
                fatPercent
                proteinPercent
                bacterialCount
                status
                totalPrice
                dateCreated
                supplier{
                    id
                    email
                }
            }
        }
    """

    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': query},
            headers={'Content-Type': 'application/json'},
            cookies=request.COOKIES  
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()

        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")
        
        milk_lots = json_data['data']['milkLotList']
     
        return render(request, 'milk_lot_list.html', {'milk_lots': milk_lots})
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Request error: {e}")


def create_milk_lot_view(request):
    tester = request.user.tester if hasattr(request.user, 'tester') else None
    sessionid = request.COOKIES.get('sessionid')
    if request.method == "POST":
        data = request.POST
        query = """
        mutation CreateMilkLot($input: MilkLotInput!) {
            createMilkLot(input: $input) {
                    supplierId
                    volumeL
                    fatPercent
                    proteinPercent
                    lactosePercent
                    totalSolids
                    snf
                    ureaNitrogen
                    bacterialCount
                }
            }
        """

        variables = {
            'input': {
                "supplierId": int(data.get("supplier_id")),
                "volumeL": float(data.get("volume_l")),
                "fatPercent": float(data.get("fat_percent")),
                "proteinPercent": float(data.get("protein_percent")),
                "lactosePercent": float(data.get("lactose_percent")),
                "totalSolids": float(data.get("total_solids")),
                "snf": float(data.get("snf")),
                "ureaNitrogen": float(data.get("urea_nitrogen")),
                "bacterialCount": int(data.get("bacterial_count")),
            }
        }

        response = requests.post(
            'http://localhost:8000/graphql/',
            json={"query": query, "variables": variables},
            headers={
                    'Content-Type': 'application/json',
                    'Cookie': f'sessionid={sessionid}',
                }
        )

        if response.status_code != 200:
                return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()
        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")
        messages.success(request, "Result for milk Lot updated successfully")
        return redirect('milk_lot_list')  
    
    GET_ALL_SUPPLIERS = """
        query {
            suppliers {
                id
                email
            }
        }
    """

    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': GET_ALL_SUPPLIERS},
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()

        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")

        suppliers = json_data['data']['suppliers']

        return render(request, "add_milk_result.html", {'suppliers':suppliers})
    except requests.exceptions.RequestException as e:
            return HttpResponse(f"Request error: {e}")
    

def edit_milk_lot(request, lot_id):
    sessionid = request.COOKIES.get('sessionid')

    if request.method == "POST":
        data = request.POST
        query = """
        mutation UpdateMilkLot($id: ID!, $input: MilkLotInput!) {
            updateMilkLot(id: $id, input: $input) {
                    id
                    volumeL
                    fatPercent
                    proteinPercent
                    lactosePercent
                    totalSolids
                    snf
                    ureaNitrogen
                    bacterialCount
            }
        }
        """

        variables = {
            'id': str(lot_id),
            'input': {
                "supplierId": int(data.get("supplier_id")),
                "volumeL": float(data.get("volume_l")),
                "fatPercent": float(data.get("fat_percent")),
                "proteinPercent": float(data.get("protein_percent")),
                "lactosePercent": float(data.get("lactose_percent")),
                "totalSolids": float(data.get("total_solids")),
                "snf": float(data.get("snf")),
                "ureaNitrogen": float(data.get("urea_nitrogen")),
                "bacterialCount": int(data.get("bacterial_count")),
            }
        }

        response = requests.post(
            'http://localhost:8000/graphql/',
            json={"query": query, "variables": variables},
            headers={
                'Content-Type': 'application/json',
                'Cookie': f'sessionid={sessionid}',
            }
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()
        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")
        milk_lot_id = json_data['data']['updateMilkLot']['id']
        messages.success(request, f"Milk Lot ID {milk_lot_id} updated successfully.")
        return redirect('milk_lot_list')
    

    GET_MILK_LOT = """
        query GetMilkLotById($id: Int!) {
            milkLotById(id: $id) {
                id
                supplierId
                volumeL
                fatPercent
                proteinPercent
                lactosePercent
                totalSolids
                snf
                ureaNitrogen
                bacterialCount
                supplier {
                    id
                    email
                    }
            }
        }
        """
    try:
        lot_response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': GET_MILK_LOT, 'variables': {'id': int(lot_id)}},
            headers={
                'Content-Type': 'application/json',
                'Cookie': f'sessionid={sessionid}'
                }
            
        )

        if lot_response.status_code != 200:
            return HttpResponse("Failed to fetch data.")

        lot_data = lot_response.json()

        if 'errors' in lot_data:
            return HttpResponse(f"GraphQL errors: {lot_data.get('errors', '')}")
        milk_lot = lot_data['data']['milkLotById']

        return render(request, "add_milk_result.html", {
            'milk_lot': milk_lot,
        })

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Request error: {e}")
    

def create_payment_bill(request):
    sessionid = request.COOKIES.get('sessionid')

    if request.method == "POST":
        data = json.loads(request.body)
        supplier_id = int(data.get("supplier_id"))
        test_date = data.get("date")
        payment_date = data.get("payment_date", None)
        is_paid = data.get("is_paid", False)
        query = """
        mutation CreatePaymentBill($input: CreatePaymentBillInput!) {
            createPaymentBill(input: $input) {
                success
                bill {
                    id
                    totalVolumeL
                    totalValue
                    isPaid
                }
                error
            }
        }
        """

        variables = {
            'input': {
                "supplierId": supplier_id,
                "date": test_date,  
                "isPaid":is_paid,
                "paymentDate": payment_date
            }
        }

        response = requests.post(
            'http://localhost:8000/graphql/',
            json={"query": query, "variables": variables},
            headers={
                'Content-Type': 'application/json',
                'Cookie': f'sessionid={sessionid}',
            }
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()
        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")
        bill = json_data['data']['createPaymentBill']['bill']
        messages.success(request, f"Payment Bill ID {bill['id']} created")
        return redirect('list_payment_bills')  

    return render(request, "payment_bill_list.html")

def payment_bill_list_view(request):
    query = """
        query {
            allPaymentBills {
                id
                date
                totalVolumeL
                totalValue
                isPaid
                paymentDate
                pdfUrl
                supplier {
                    id
                    email
                }
            }
        }
    """
    GET_ALL_SUPPLIERS = """
        query {
            suppliers {
                id
                email
            }
        }
    """

    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': GET_ALL_SUPPLIERS},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()

        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")

        suppliers = json_data['data']['suppliers']

        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': query},
            headers={'Content-Type': 'application/json'},
            cookies=request.COOKIES
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()

        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")

        payment_bills = json_data['data']['allPaymentBills']
        
        return render(request, 'payment_bill_list.html', {'payment_bills': payment_bills,'suppliers':suppliers})

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Request error: {e}")
    

def get_payment_bill_by_id(request, bill_id):
    sessionid = request.COOKIES.get('sessionid')

    query = """
    query GetPaymentBillById($id: Int!) {
        paymentBillById(id: $id) {
            id
            date
            totalVolumeL
            totalValue
            isPaid
            paymentDate
            pdfUrl
            supplier {
                id
                email
            }
        }
    }
    """

    variables = {
        "id": int(bill_id)
    }

    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': query, 'variables': variables},
            headers={
                'Content-Type': 'application/json',
                'Cookie': f'sessionid={sessionid}',
            }
        )

        if response.status_code != 200:
            return HttpResponse(f"GraphQL request failed with status {response.status_code}<br><br>{response.text}")

        json_data = response.json()

        if 'errors' in json_data:
            return HttpResponse(f"GraphQL errors: {json_data['errors']}")

        bill_data = json_data['data']['paymentBillById']

        if not bill_data:
            messages.error(request, f"No payment bill found with ID {bill_id}")
            return render(request, "payment_bill_detail.html", {'bill': None})

        return JsonResponse({'bill': bill_data})
    
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Request error: {e}")
