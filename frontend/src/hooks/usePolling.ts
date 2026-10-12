import { useEffect, useState } from "react";

export default function usePolling<T>(
    fetcher: () => Promise<T>,
    interval: number
) {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState(false);

    useEffect(() => {
        let active = true;
        let timer: ReturnType<typeof setTimeout>;

        async function update() {
            try {
                const result = await fetcher();

                if (active) {
                    setData(result);
                    setError(false);
                }
            } catch {
                if (active) {
                    setError(true);
                }
            } finally {
                if (active) {
                    timer = setTimeout(() => {
                        void update();
                    }, interval);
                }
            }
        }

        void update();

        return () => {
            active = false;
            clearTimeout(timer);
        };
    }, [fetcher, interval]);

    return { data, error };
}