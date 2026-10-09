import type { MemoryResponse } from "../services/api";

interface MemoryCardProps {
    memory: MemoryResponse | null;
}

export default function MemoryCard({ memory }: MemoryCardProps) {
    if (memory === null) {
        return <p>Loading memory information...</p>;
    }

    const toGiB = (bytes: number): string => {
        return (bytes / (1024 ** 3)).toFixed(1);
    };

    return (
        <div>
            <h2>Memory</h2>

            <p>Usage: {memory.percent.toFixed(1)}%</p>

            <p>Used: {toGiB(memory.used)} GiB</p>

            <p>Available: {toGiB(memory.available)} GiB</p>

            <p>Total: {toGiB(memory.total)} GiB</p>
        </div>
    );
}