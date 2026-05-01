const express = require('express')
const router = express.Router()

/**
 * Returns all users with optional pagination
 */
router.get('/users', (req, res) => {
    const { limit, skip } = req.query
    res.json([])
})

/**
 * Returns a single user by ID
 */
router.get('/users/:id', (req, res) => {
    res.json({})
})

/**
 * Creates a new user account
 */
router.post('/users', (req, res) => {
    const { name, email, age } = req.body
    res.json({})
})

/**
 * Updates an existing user
 */
router.put('/users/:id', (req, res) => {
    const { name, email } = req.body
    res.json({})
})

/**
 * Deletes a user by ID
 */
router.delete('/users/:id', (req, res) => {
    res.json({ success: true })
})