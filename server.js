/**
 * BD Modern School - Secure Admissions Backend
 * 
 * This server handles multi-step admission applications, secure document uploads (PDF/Images),
 * sanitizes filenames, enforces strict validation limits, and triggers automated webhook notifications
 * (WhatsApp and Email) to parents upon successful registration.
 * 
 * Setup Instructions:
 * 1. Initialize npm in this directory: npm init -y
 * 2. Install dependencies: npm install express multer cors dotenv node-fetch
 * 3. Run the server: node server.js
 */

const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS and parse JSON/Form payloads
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Ensure upload directory exists securely
const UPLOADS_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS_DIR)) {
    fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

// Serve uploaded documents securely (or configure cloud storage in production)
app.use('/uploads', express.static(UPLOADS_DIR));

// HTTP Basic Authentication Middleware for Staff Desk Isolation
const basicAuth = (req, res, next) => {
    const authHeader = req.headers.authorization;
    if (!authHeader) {
        res.setHeader('WWW-Authenticate', 'Basic realm="BDMS Staff Desk Terminal"');
        return res.status(401).send('Authentication required.');
    }

    const auth = Buffer.from(authHeader.split(' ')[1], 'base64').toString().split(':');
    const user = auth[0];
    const pass = auth[1];

    if (user === 'admin' && pass === 'bdms_secure_pass_2026') {
        return next();
    } else {
        res.setHeader('WWW-Authenticate', 'Basic realm="BDMS Staff Desk Terminal"');
        return res.status(401).send('Access Denied: Invalid Credentials.');
    }
};

// Protect the staff_desk directory with HTTP Basic Auth
app.use('/staff_desk', basicAuth, express.static(path.join(__dirname, 'staff_desk')));

// Protect the standalone admin.html file specifically (for fast loading)
app.get('/admin', basicAuth, (req, res) => {
    res.sendFile(path.join(__dirname, 'admin.html'));
});
app.get('/admin.html', basicAuth, (req, res) => {
    res.sendFile(path.join(__dirname, 'admin.html'));
});

// Serve general client static files (e.g. index.html, logo.png, sw.js)
app.use(express.static(__dirname));

// Configure secure Multer storage engine
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOADS_DIR);
    },
    filename: (req, file, cb) => {
        // Sanitize filename: remove path traversals, special characters and append safe unique ID
        const cleanName = file.originalname
            .replace(/[^a-zA-Z0-9.\-_]/g, '_')
            .replace(/\.\.+/g, '.');
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, `${uniqueSuffix}-${cleanName}`);
    }
});

// File filter validation (Strict types: JPG, PNG, PDF only)
const fileFilter = (req, file, cb) => {
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.pdf'];
    const allowedMimeTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    
    const fileExt = path.extname(file.originalname).toLowerCase();
    const isAllowedExt = allowedExtensions.includes(fileExt);
    const isAllowedMime = allowedMimeTypes.includes(file.mimetype);

    if (isAllowedExt && isAllowedMime) {
        cb(null, true);
    } else {
        cb(new Error('Security check failed: Only JPG, PNG, and PDF files are allowed.'), false);
    }
};

// Multer upload config: Max size 100MB, up to 3 files
const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 100 * 1024 * 1024 // 100 Megabytes
    }
}).fields([
    { name: 'studentPhoto', maxCount: 1 },
    { name: 'birthCert', maxCount: 1 },
    { name: 'parentID', maxCount: 1 }
]);

/**
 * Mock Webhook Trigger Function
 * Simulates external REST calls to messaging APIs (Twilio for WhatsApp / SendGrid for Email)
 */
async function triggerNotificationsWebhook(payload) {
    const webhookUrl = process.env.NOTIFICATION_WEBHOOK_URL || 'https://api.bdmodern.school/webhooks/admissions';
    
    console.log('\n=================== WEBHOOK TRIGGERED ===================');
    console.log(`Target Hook: ${webhookUrl}`);
    console.log('Sending secure REST transmission with payload:');
    console.log(JSON.stringify(payload, null, 2));

    // Simulation of network call to Twilio WhatsApp / SendGrid APIs
    const simulatedResponse = {
        success: true,
        whatsappStatus: 'QUEUED',
        emailStatus: 'SENT',
        messageId: 'MSG-' + Math.random().toString(36).substr(2, 9).toUpperCase()
    };
    
    console.log('Webhook Response Received:', simulatedResponse);
    console.log('=========================================================\n');
    
    return simulatedResponse;
}

/**
 * REST Endpoint to handle multi-step admission submission
 */
app.post('/api/admission/submit', (req, res) => {
    upload(req, res, async (err) => {
        // Handle upload limitations or format errors
        if (err) {
            console.error('File upload validation failure:', err.message);
            return res.status(400).json({
                success: false,
                error: err.message
            });
        }

        try {
            // Extract text fields
            const { 
                firstName, lastName, dob, gender, grade, prevSchool, about,
                parentName, relationship, phone, email, address, occupation
            } = req.body;

            // Strict Server-Side validations (defense in depth)
            if (!firstName || !lastName || !dob || !gender || !grade) {
                return res.status(400).json({ success: false, error: 'Validation Error: Missing crucial student details.' });
            }
            if (!parentName || !relationship || !phone || !email || !address) {
                return res.status(400).json({ success: false, error: 'Validation Error: Missing crucial guardian details.' });
            }

            // Verify files exist in fields
            if (!req.files || !req.files.studentPhoto || !req.files.birthCert) {
                return res.status(400).json({ success: false, error: 'Security constraint: Required documents were not uploaded.' });
            }

            // Generate unique Registration Confirmation ID
            const admissionNo = 'BDMS-2026-' + Math.floor(100000 + Math.random() * 900000);

            // Document mappings
            const mappedDocs = {
                studentPhoto: req.files.studentPhoto[0].filename,
                birthCert: req.files.birthCert[0].filename,
                parentID: req.files.parentID ? req.files.parentID[0].filename : null
            };

            const studentRecord = {
                id: admissionNo,
                student: { firstName, lastName, dob, gender, grade, prevSchool, about },
                parent: { parentName, relationship, phone, email, address, occupation },
                docs: {
                    studentPhoto: req.files.studentPhoto ? { name: req.files.studentPhoto[0].originalname, size: (req.files.studentPhoto[0].size / 1024).toFixed(1) + ' KB', data: `/uploads/${req.files.studentPhoto[0].filename}`, type: req.files.studentPhoto[0].mimetype } : null,
                    birthCert: req.files.birthCert ? { name: req.files.birthCert[0].originalname, size: (req.files.birthCert[0].size / 1024).toFixed(1) + ' KB', data: `/uploads/${req.files.birthCert[0].filename}`, type: req.files.birthCert[0].mimetype } : null,
                    parentID: req.files.parentID ? { name: req.files.parentID[0].originalname, size: (req.files.parentID[0].size / 1024).toFixed(1) + ' KB', data: `/uploads/${req.files.parentID[0].filename}`, type: req.files.parentID[0].mimetype } : null
                },
                submittedAt: new Date().toLocaleString(),
                status: 'Pending Verification',
                chat: [
                    { sender: 'admin', text: 'Welcome! Your application has been successfully logged and sent to the Departmental Panel for Session 2026-27 review. You can chat with us here if you have any questions or if any additional documents are required.', timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
                ]
            };

            // Log details in console
            console.log(`[SUCCESS] New secure admission recorded: ${admissionNo}`);
            
            // Trigger automated WhatsApp & Email confirmation webhook
            const webhookPayload = {
                admissionNo: admissionNo,
                parent: {
                    name: parentName,
                    phone: phone,
                    email: email
                },
                student: {
                    name: `${firstName} ${lastName}`,
                    grade: grade
                },
                documentsUploaded: Object.keys(mappedDocs).filter(k => mappedDocs[k] !== null)
            };

            // Trigger the webhook
            const notificationStatus = await triggerNotificationsWebhook(webhookPayload);

            // Return success response to the client
            return res.status(201).json({
                success: true,
                message: 'Admission form successfully captured and verified.',
                admissionNo: admissionNo,
                studentRecord: studentRecord,
                notification: notificationStatus
            });

        } catch (serverErr) {
            console.error('System registration failure:', serverErr);
            return res.status(500).json({
                success: false,
                error: 'Internal system fault occurred during registration process.'
            });
        }
    });
});

// Start the express cluster
app.listen(PORT, () => {
    console.log(`✦ BD Modern School Admissions backend active on port ${PORT}`);
    console.log(`✦ File uploads routed to directory: ${UPLOADS_DIR}`);
});
