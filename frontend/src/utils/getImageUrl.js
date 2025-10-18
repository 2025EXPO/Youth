import BASE_URL from "../config";

export const getImageUrl = (path) => {
    if (!path) return "";
    return path.startsWith("http")
        ? path
        : `${BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
};
