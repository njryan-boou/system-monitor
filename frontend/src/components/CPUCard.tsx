interface CPUCardProps {
    usage: number | null;
}

export default function CPUCard({ usage }: CPUCardProps) {
    return (
        <div>
            <h2>CPU</h2>

            <p>
                {usage === null ? "Loading cpu usage..." : `${usage.toFixed(1)}%`}
            </p>
        </div>
    );
}