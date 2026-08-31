// ping-server.js
const RENDER_API_URL = 'https://ems-vxmk.onrender.com';

export default async function (req, context) {
    try {
        console.log("Pinging Render Server at:", RENDER_API_URL);

        const response = await fetch(RENDER_API_URL);

        if (response.ok) {
            console.log(`Ping successful! Status: ${response.status}`);
        } else {
            console.log(`Ping failed with status: ${response.status}`);
        }

        // V2 API-তে Response অবজেক্ট রিটার্ন করতে হয়
        return new Response(JSON.stringify({ message: "Ping executed successfully" }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });

    } catch (error) {
        console.error("Error pinging the server:", error.message);
        return new Response(JSON.stringify({ error: "Failed to ping server" }), {
            status: 500,
            headers: { "Content-Type": "application/json" }
        });
    }
};

// শিডিউলটি আলাদাভাবে এক্সপোর্ট করতে হয়
export const config = {
    schedule: "*/10 * * * *" // Every 10 minutes
};