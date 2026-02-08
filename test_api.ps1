# API Testing Script for Dino Ventures Wallet Service
# Tests all endpoints with comprehensive validation

$baseUrl = "http://localhost:8001"
$apiUrl = "$baseUrl/api/v1"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "API ENDPOINT TESTING - Dino Ventures Wallet Service" -ForegroundColor Cyan
Write-Host "Base URL: $baseUrl" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Test counter
$testNumber = 0
$passedTests = 0
$failedTests = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [object]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    $script:testNumber++
    Write-Host "`n[$script:testNumber] Testing: $Name" -ForegroundColor Yellow
    Write-Host "    Method: $Method" -ForegroundColor Gray
    Write-Host "    URL: $Url" -ForegroundColor Gray
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            Write-Host "    Body: $jsonBody" -ForegroundColor Gray
            $response = Invoke-WebRequest -Uri $Url -Method $Method -Headers $headers -Body $jsonBody -UseBasicParsing
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method $Method -Headers $headers -UseBasicParsing
        }
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "    ✓ PASSED - Status: $($response.StatusCode)" -ForegroundColor Green
            $script:passedTests++
            
            # Parse and display response
            $responseData = $response.Content | ConvertFrom-Json
            Write-Host "    Response:" -ForegroundColor Cyan
            Write-Host "    $(($responseData | ConvertTo-Json -Depth 5))" -ForegroundColor White
            
            return $responseData
        } else {
            Write-Host "    ✗ FAILED - Expected: $ExpectedStatus, Got: $($response.StatusCode)" -ForegroundColor Red
            $script:failedTests++
        }
    } catch {
        Write-Host "    ✗ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:failedTests++
        if ($_.Exception.Response) {
            $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
            $errorBody = $reader.ReadToEnd()
            Write-Host "    Error Details: $errorBody" -ForegroundColor Red
        }
    }
}

# ============================================================
# TEST 1: Health Check
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 1: HEALTH AND SYSTEM ENDPOINTS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Test-Endpoint -Name "Health Check" -Method "GET" -Url "$baseUrl/health"

# ============================================================
# TEST 2: List All Users
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 2: USER MANAGEMENT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Test-Endpoint -Name "List All Users" -Method "GET" -Url "$apiUrl/users"

# ============================================================
# TEST 3: Get User Accounts
# ============================================================
Test-Endpoint -Name "Get User Accounts (user_001)" -Method "GET" -Url "$apiUrl/users/user_001/accounts"

Test-Endpoint -Name "Get User Accounts (user_002)" -Method "GET" -Url "$apiUrl/users/user_002/accounts"

# ============================================================
# TEST 4: Get Wallet Balances
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 3: WALLET BALANCE QUERIES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Test-Endpoint -Name "Get Balance (user_001)" -Method "GET" -Url "$apiUrl/wallets/user_001/balance"

Test-Endpoint -Name "Get Balance (user_002)" -Method "GET" -Url "$apiUrl/wallets/user_002/balance"

# ============================================================
# TEST 5: Wallet Top-up Transaction
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 4: WALLET TOP-UP (Purchase Credits)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$topupRequest = @{
    user_id = "user_001"
    asset_type = "GOLD_COINS"
    amount = "100.00"
    idempotency_key = "test_topup_$(Get-Date -Format 'yyyyMMddHHmmss')"
    metadata = @{
        payment_id = "pay_test_001"
        payment_method = "credit_card"
    }
}

$topupResult = Test-Endpoint -Name "Create Top-up Transaction" -Method "POST" -Url "$apiUrl/transactions/topup" -Body $topupRequest

# Save transaction ID for later
$topupTxnId = $topupResult.id

# ============================================================
# TEST 6: Bonus Transaction
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 5: BONUS/INCENTIVE TRANSACTIONS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$bonusRequest = @{
    user_id = "user_002"
    asset_type = "LOYALTY_POINTS"
    amount = "25.00"
    idempotency_key = "test_bonus_$(Get-Date -Format 'yyyyMMddHHmmss')"
    metadata = @{
        reason = "referral_bonus"
        referral_code = "REF12345"
    }
}

$bonusResult = Test-Endpoint -Name "Create Bonus Transaction" -Method "POST" -Url "$apiUrl/transactions/bonus" -Body $bonusRequest

$bonusTxnId = $bonusResult.id

# ============================================================
# TEST 7: Spend Transaction
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 6: SPEND/PURCHASE TRANSACTIONS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$spendRequest = @{
    user_id = "user_001"
    asset_type = "GOLD_COINS"
    amount = "50.00"
    idempotency_key = "test_spend_$(Get-Date -Format 'yyyyMMddHHmmss')"
    metadata = @{
        item_id = "item_premium_skin_001"
        item_name = "Dragon Armor Skin"
        quantity = 1
    }
}

$spendResult = Test-Endpoint -Name "Create Spend Transaction" -Method "POST" -Url "$apiUrl/transactions/spend" -Body $spendRequest

$spendTxnId = $spendResult.id

# ============================================================
# TEST 8: Idempotency Test
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 7: IDEMPOTENCY VERIFICATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nTesting idempotency by sending duplicate top-up request..." -ForegroundColor Yellow

$duplicateTopup = @{
    user_id = "user_001"
    asset_type = "DIAMONDS"
    amount = "200.00"
    idempotency_key = "idempotency_test_duplicate_001"
    metadata = @{
        test = "first_request"
    }
}

$firstRequest = Test-Endpoint -Name "First Request (New Transaction)" -Method "POST" -Url "$apiUrl/transactions/topup" -Body $duplicateTopup

# Send exact same request again
Start-Sleep -Milliseconds 500

$secondRequest = Test-Endpoint -Name "Second Request (Duplicate - Should Return Same ID)" -Method "POST" -Url "$apiUrl/transactions/topup" -Body $duplicateTopup

if ($firstRequest.id -eq $secondRequest.id) {
    Write-Host "`n    ✓ IDEMPOTENCY VERIFIED - Both requests returned same transaction ID: $($firstRequest.id)" -ForegroundColor Green
    $script:passedTests++
} else {
    Write-Host "`n    ✗ IDEMPOTENCY FAILED - Different transaction IDs returned!" -ForegroundColor Red
    $script:failedTests++
}

# ============================================================
# TEST 9: Get Specific Transaction
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 8: TRANSACTION RETRIEVAL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if ($topupTxnId) {
    Test-Endpoint -Name "Get Transaction by ID (Topup)" -Method "GET" -Url "$apiUrl/transactions/$topupTxnId"
}

if ($spendTxnId) {
    Test-Endpoint -Name "Get Transaction by ID (Spend)" -Method "GET" -Url "$apiUrl/transactions/$spendTxnId"
}

# ============================================================
# TEST 10: Transaction History
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 9: TRANSACTION HISTORY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Test-Endpoint -Name "Get Transaction History (user_001)" -Method "GET" -Url "$apiUrl/wallets/user_001/transactions?limit=10&offset=0"

Test-Endpoint -Name "Get Transaction History (user_002)" -Method "GET" -Url "$apiUrl/wallets/user_002/transactions?limit=5&offset=0"

# ============================================================
# TEST 11: Error Handling - Insufficient Balance
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 10: ERROR HANDLING AND VALIDATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$insufficientBalanceRequest = @{
    user_id = "user_002"
    asset_type = "GOLD_COINS"
    amount = "999999.00"
    idempotency_key = "test_insufficient_$(Get-Date -Format 'yyyyMMddHHmmss')"
    metadata = @{}
}

Write-Host "`n[$script:testNumber] Testing: Insufficient Balance Error" -ForegroundColor Yellow
try {
    $headers = @{ "Content-Type" = "application/json" }
    $jsonBody = $insufficientBalanceRequest | ConvertTo-Json -Depth 10
    Invoke-WebRequest -Uri "$apiUrl/transactions/spend" -Method "POST" -Headers $headers -Body $jsonBody -UseBasicParsing | Out-Null
    Write-Host "    ✗ FAILED - Should have returned error for insufficient balance" -ForegroundColor Red
    $script:failedTests++
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-Host "    ✓ PASSED - Correctly returned 400 error for insufficient balance" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host "    ✗ FAILED - Wrong status code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        $script:failedTests++
    }
}

# ============================================================
# TEST 12: Final Balance Check
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SECTION 11: FINAL BALANCE VERIFICATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$finalBalance = Test-Endpoint -Name "Final Balance Check (user_001)" -Method "GET" -Url "$apiUrl/wallets/user_001/balance"

# ============================================================
# SUMMARY
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$totalTests = $passedTests + $failedTests

Write-Host "`nTotal Tests Run: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })

if ($failedTests -eq 0) {
    Write-Host "`n✓ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "The Dino Ventures Wallet Service is working perfectly!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Some tests failed. Please review the errors above." -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
