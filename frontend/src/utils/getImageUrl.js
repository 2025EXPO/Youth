export const getImageUrl = (path) => {
    const base = "http://13.208.215.216:5000";
    if (!path) return "";
    return path.startsWith("http")
        ? path
        : `${base}${path.startsWith("/") ? "" : "/"}${path}`;
};
