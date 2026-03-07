#!/bin/bash
# Endpoint Testing Script for Vercel Deployment
# Tests all API endpoints after deployment
# Usage: ./TEST_ENDPOINTS.sh https://your-deployment.vercel.app

API_URL="${1:-http://localhost:3000}"
TEMP_EMAIL="testuser-$(date +%s)@gmail.com"
TEMP_PASSWORD="Test123"
TEMP_TOKEN=""

echo "🧪 Testing Vercel Deployment Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API URL: $API_URL"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

# Test helper function
test_endpoint() {
    local name="$1"
    local method="$2"
    local path="$3"
    local data="$4"
    local expected_status="$5"
    local headers="${6:--H \"Content-Type: application/json\"}"
    
    test_count=$((test_count + 1))
    
    echo -n "Test $test_count: $name ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL$path" $headers)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$path" $headers -d "$data")
    fi
    
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [[ "$status" == *"$expected_status"* ]]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status)"
        pass_count=$((pass_count + 1))
        echo "$body" | head -c 100
        echo ""
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status)"
        fail_count=$((fail_count + 1))
        echo "Response: $body" | head -c 100
        echo ""
    fi
}

# Extract token from response
extract_token() {
    echo "$1" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4
}

# ============================================================================
# PHASE 1: Authentication Tests
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 1: Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test CORS preflight
echo "Checking CORS support..."
cors_response=$(curl -s -i -X OPTIONS "$API_URL/api/auth/signup")
if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✅ CORS headers present${NC}"
    pass_count=$((pass_count + 1))
else
    echo -e "${RED}❌ CORS headers missing${NC}"
    fail_count=$((fail_count + 1))
fi
test_count=$((test_count + 1))
echo ""

# Test signup with public email
test_endpoint "Signup with public email" "POST" "/api/auth/signup" \
    "{\"email\":\"$TEMP_EMAIL\",\"password\":\"$TEMP_PASSWORD\",\"full_name\":\"Test User\"}" "201"

# Extract token for later use
signup_response=$(curl -s -X POST "$API_URL/api/auth/signup" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEMP_EMAIL\",\"password\":\"$TEMP_PASSWORD\",\"full_name\":\"Test User\"}")
TEMP_TOKEN=$(extract_token "$signup_response")

if [ -z "$TEMP_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  Could not extract token from signup response${NC}"
    echo "Response: $signup_response"
else
    echo -e "${GREEN}✅ Token extracted: ${TEMP_TOKEN:0:20}...${NC}"
    pass_count=$((pass_count + 1))
fi
test_count=$((test_count + 1))
echo ""

# Test signin
test_endpoint "Signin with credentials" "POST" "/api/auth/signin" \
    "{\"email\":\"$TEMP_EMAIL\",\"password\":\"$TEMP_PASSWORD\"}" "200"
echo ""

# ============================================================================
# PHASE 2: Feature Tests (require authentication)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 2: Features (Authenticated)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$TEMP_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  Skipping authenticated tests (no token)${NC}"
else
    auth_header="-H \"Content-Type: application/json\" -H \"Authorization: Bearer $TEMP_TOKEN\""
    
    # Test translation
    test_endpoint "Translate to Urdu" "POST" "/api/translate" \
        "{\"text\":\"Hello world\",\"target_language\":\"ur\"}" "200" "$auth_header"
    echo ""
    
    # Test personalization
    test_endpoint "Personalize content" "POST" "/api/personalize" \
        "{\"content\":\"ROS is a framework\",\"learning_level\":\"beginner\"}" "200" "$auth_header"
    echo ""
    
    # Test chat
    test_endpoint "Chat with RAG" "POST" "/api/chat" \
        "{\"message\":\"What is ROS?\",\"conversation_id\":\"123e4567-e89b-12d3-a456-426614174000\"}" "200" "$auth_header"
    echo ""
fi

# ============================================================================
# PHASE 3: Error Handling
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 3: Error Handling"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test invalid email
test_endpoint "Signup with invalid email" "POST" "/api/auth/signup" \
    "{\"email\":\"not-an-email\",\"password\":\"Test123\",\"full_name\":\"Test\"}" "400"
echo ""

# Test weak password
test_endpoint "Signup with weak password" "POST" "/api/auth/signup" \
    "{\"email\":\"user@gmail.com\",\"password\":\"test\",\"full_name\":\"Test\"}" "400"
echo ""

# Test missing token
test_endpoint "Translate without token" "POST" "/api/translate" \
    "{\"text\":\"Hello\",\"target_language\":\"ur\"}" "401"
echo ""

# Test invalid token
test_endpoint "Chat with invalid token" "POST" "/api/chat" \
    "{\"message\":\"Test\"}" "401" \
    "-H \"Content-Type: application/json\" -H \"Authorization: Bearer invalid_token_xyz\""
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total Tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
