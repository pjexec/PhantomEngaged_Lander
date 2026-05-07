const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Parse JSON request bodies
app.use(express.json());

// ── ActiveCampaign subscribe endpoint ──────────────────────
app.post('/api/subscribe', async (req, res) => {
  const { firstName, email } = req.body;

  if (!email || !firstName) {
    return res.status(400).json({ success: false, error: 'First name and email are required.' });
  }

  // Basic email format check
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ success: false, error: 'Please enter a valid email address.' });
  }

  const AC_API_URL = process.env.AC_API_URL;
  const AC_API_KEY = process.env.AC_API_KEY;
  const AC_LIST_ID = process.env.AC_LIST_ID || '13';

  if (!AC_API_URL || !AC_API_KEY) {
    console.error('ActiveCampaign environment variables not configured');
    return res.status(500).json({ success: false, error: 'Server configuration error.' });
  }

  const headers = {
    'Api-Token': AC_API_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  try {
    // Step 1: Create or update the contact via sync endpoint
    const syncRes = await fetch(`${AC_API_URL}/api/3/contact/sync`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        contact: {
          email: email.trim().toLowerCase(),
          firstName: firstName.trim()
        }
      })
    });

    if (!syncRes.ok) {
      const errBody = await syncRes.text();
      console.error('AC contact sync failed:', syncRes.status, errBody);
      return res.status(502).json({ success: false, error: 'Could not save your information. Please try again.' });
    }

    const syncData = await syncRes.json();
    const contactId = syncData.contact?.id;

    if (!contactId) {
      console.error('AC contact sync returned no contact ID:', syncData);
      return res.status(502).json({ success: false, error: 'Unexpected response from server. Please try again.' });
    }

    // Step 2: Add contact to the specified list
    const listRes = await fetch(`${AC_API_URL}/api/3/contactLists`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        contactList: {
          list: AC_LIST_ID,
          contact: contactId,
          status: 1  // 1 = active/subscribed
        }
      })
    });

    if (!listRes.ok) {
      const errBody = await listRes.text();
      console.error('AC list add failed:', listRes.status, errBody);
      // Contact was created, list add failed — not a total failure
    }

    // Step 3: Add tag "phantom-engaged-download"
    // First, find or create the tag
    let tagId;

    const tagSearchRes = await fetch(`${AC_API_URL}/api/3/tags?search=phantom-engaged-download`, {
      method: 'GET',
      headers
    });

    if (tagSearchRes.ok) {
      const tagSearchData = await tagSearchRes.json();
      const existingTag = tagSearchData.tags?.find(t => t.tag === 'phantom-engaged-download');

      if (existingTag) {
        tagId = existingTag.id;
      } else {
        // Create the tag
        const tagCreateRes = await fetch(`${AC_API_URL}/api/3/tags`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            tag: {
              tag: 'phantom-engaged-download',
              tagType: 'contact',
              description: 'Downloaded the Phantom Engaged position paper'
            }
          })
        });

        if (tagCreateRes.ok) {
          const tagCreateData = await tagCreateRes.json();
          tagId = tagCreateData.tag?.id;
        }
      }
    }

    // Apply tag to contact
    if (tagId) {
      await fetch(`${AC_API_URL}/api/3/contactTags`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          contactTag: {
            contact: contactId,
            tag: tagId
          }
        })
      });
    }

    return res.json({ success: true });

  } catch (err) {
    console.error('Subscribe endpoint error:', err);
    return res.status(500).json({ success: false, error: 'Something went wrong. Please try again.' });
  }
});

// ── Serve static files ─────────────────────────────────────
app.use(express.static(path.join(__dirname), {
  extensions: ['html'],
  maxAge: '1h',
  setHeaders: (res, filePath) => {
    if (filePath.endsWith('.pdf')) {
      res.setHeader('Content-Type', 'application/pdf');
    }
    // HTML files: no cache — ensures crawlers always get fresh meta tags
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
    }
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  }
}));

// SPA fallback — also no-cache for the HTML response
app.get('*', (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Phantom Engaged lander running on port ${PORT}`);
});
