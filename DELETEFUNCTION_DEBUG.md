# Delete Function Debugging Guide

## Issue
The delete function is not working in the SellerPage.

## What I've Verified ✅

### Backend (All Correct)
1. ✅ Delete endpoint exists at `DELETE /api/products/{product_id}`
2. ✅ Endpoint checks authentication via `get_current_user` dependency
3. ✅ Endpoint verifies product ownership (seller_id must match user_id)
4. ✅ Endpoint deletes product from Firestore
5. ✅ Endpoint cleans up Cloudinary images
6. ✅ Returns 200 with success message

### Frontend API Layer (All Correct)
1. ✅ `api-service.ts` has `deleteProduct` function
2. ✅ Uses `del()` from api-client which adds auth token automatically
3. ✅ Logs request and response for debugging

### Frontend Hook Layer (All Correct)
1. ✅ `useDeleteProduct` hook exists in `useProducts.ts`
2. ✅ Calls `api.deleteProduct(productId)`
3. ✅ Has optimistic updates
4. ✅ Invalidates React Query cache on success
5. ✅ Shows toast notifications

### Frontend UI Layer (All Correct)
1. ✅ Delete button exists in SellerPage
2. ✅ Calls `handleDelete(product.id)` on click
3. ✅ Shows confirmation modal
4. ✅ Modal has "Confirm" button that calls `confirmDelete()`
5. ✅ `confirmDelete` calls `deleteProductMutation.mutateAsync(deleteProductId)`

## How to Debug

### Step 1: Open Browser DevTools
1. Open your app in Chrome/Firefox
2. Press F12 to open DevTools
3. Go to the "Console" tab
4. Go to the "Network" tab

### Step 2: Try to Delete a Product
1. Go to Seller Dashboard
2. Click the trash icon on any product
3. Click "Confirm" in the modal

### Step 3: Check Console Logs
Look for these log messages in order:

```
[SellerPage] Deleting product: <product-id>
[Hook] useDeleteProduct mutationFn called: { productId: '<product-id>' }
[API] deleteProduct called: { productId: '<product-id>' }
[API Client] DELETE request: { url: '/products/<product-id>', config: {...} }
[API Client] DELETE response: { url: '/products/<product-id>', status: 200, data: {...} }
[API] deleteProduct response: { message: 'Product deleted successfully', ... }
[Hook] useDeleteProduct onSuccess: { message: 'Product deleted successfully', ... }
[Hook] Removed product from cache, new count: <number>
[Hook] useDeleteProduct onSettled - invalidating queries
[SellerPage] Delete successful
```

### Step 4: Check Network Tab
1. Look for a request to `DELETE http://localhost:8000/api/products/<product-id>`
2. Check the request headers - should have `Authorization: Bearer <token>`
3. Check the response:
   - **200 OK** = Success
   - **401 Unauthorized** = Auth token missing or invalid
   - **403 Forbidden** = User doesn't own this product
   - **404 Not Found** = Product doesn't exist
   - **500 Internal Server Error** = Backend error

## Common Issues & Solutions

### Issue 1: 401 Unauthorized
**Cause**: Auth token not being sent or is invalid

**Solution**:
1. Check if user is logged in: `console.log(auth.currentUser)`
2. Check if token is valid: `auth.currentUser.getIdToken().then(console.log)`
3. Verify Firebase config in `.env` file

### Issue 2: 403 Forbidden
**Cause**: User doesn't own the product they're trying to delete

**Solution**:
1. Check if the product's `seller_id` matches the current user's Firebase UID
2. Log the product data: `console.log(product)`
3. Log the current user: `console.log(auth.currentUser.uid)`

### Issue 3: Network Error / CORS
**Cause**: Backend not running or CORS misconfigured

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check backend logs for CORS errors
3. Verify `VITE_API_URL` in frontend `.env` matches backend URL

### Issue 4: Nothing Happens (No Logs)
**Cause**: JavaScript error preventing execution

**Solution**:
1. Check Console for red error messages
2. Check if modal is actually showing
3. Verify `deleteProductMutation` is defined: `console.log(deleteProductMutation)`

### Issue 5: Product Deleted But UI Not Updating
**Cause**: React Query cache not invalidating

**Solution**:
1. Check if `onSettled` is being called in the hook
2. Manually refetch: `queryClient.invalidateQueries({ queryKey: ['products', 'seller'] })`
3. Hard refresh the page (Ctrl+Shift+R)

## Quick Test Script

Add this to your browser console to test the delete function directly:

```javascript
// Get the current user's token
const token = await firebase.auth().currentUser.getIdToken();

// Make a delete request
fetch('http://localhost:8000/api/products/YOUR_PRODUCT_ID', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));
```

## What to Report Back

Please share:
1. Console logs (all messages starting with `[SellerPage]`, `[Hook]`, `[API]`)
2. Network tab screenshot showing the DELETE request
3. Response status code and body
4. Any red error messages in console

This will help me identify exactly where the issue is occurring.
