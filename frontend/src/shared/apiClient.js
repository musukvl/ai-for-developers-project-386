export class ApiError extends Error {
    code;
    constructor(code, message) {
        super(message);
        this.code = code;
    }
}
let userName = '';
export function setApiUserName(name) {
    userName = name;
}
export async function api(path, options = {}) {
    const headers = new Headers(options.headers);
    if (userName)
        headers.set('X-User-Name', userName);
    if (options.body)
        headers.set('Content-Type', 'application/json');
    const response = await fetch(`/api${path}`, { ...options, headers });
    if (response.status === 204)
        return undefined;
    const body = await response.json();
    if (!response.ok)
        throw new ApiError(body.error.code, body.error.message);
    return body;
}
