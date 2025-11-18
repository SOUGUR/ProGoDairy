
// ========================================== Memory-stored access token ============================================================
let ACCESS_TOKEN = null;

//================================================ Normal GraphQL call function ============================================================================
async function callGraphQL(query, variables = {}) {
    const response = await fetch("/graphql/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('csrftoken'),
        },
        body: JSON.stringify({ query, variables }),
    });

    return response.json();
}

// ===================================================== fetch cookie ======================================================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ======================================================== SECURED GRAPHQL call for queries and mutation (Access Token + Refresh Token) =====================
async function securedGraphQL(query, variables = {}) {
    const response = await fetch("/graphql/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + ACCESS_TOKEN,
        },
        body: JSON.stringify({ query, variables }),
    });

    const data = await response.json();
    if (data.errors && data.errors[0].message.includes("Signature has expired")) {
        const refreshQuery = `
            mutation {
                refreshAccess {
                    accessToken
                }
            }
        `;

        const refreshResult = await callGraphQL(refreshQuery);

        ACCESS_TOKEN = refreshResult.data.refreshAccess.accessToken;

        return securedGraphQL(query, variables);
    }

    return data;
}

// =================================================== gets a new access token =====================================================================
async function initializeAccessToken() {
    const refreshQuery = `
        mutation {
            refreshAccess {
                accessToken
            }
        }
    `;

    try {
        const result = await callGraphQL(refreshQuery);

        ACCESS_TOKEN = result.data.refreshAccess.accessToken;
        return true;
    } catch (err) {
        console.warn("Not logged in, redirecting…");
        window.location.href = "/";
        return false;
    }
}

