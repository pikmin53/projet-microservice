import {LineChart,Line,XAxis,YAxis,Tooltip,CartesianGrid} from "recharts"

export default function MetricsChart({data,title}){
    const metricKeys = data.length > 0 ? Object.keys(data[0]).filter(key => key !== 'time') : [];

    return(
        <div style={{marginBottom:40}}>
            <h3>{title}</h3>

            <LineChart width={700} height={300} data={data}>
                <CartesianGrid strokeDasharray="3 3"/>
                <XAxis dataKey="time"/>
                <YAxis/>
                <Tooltip/>

                {metricKeys.map(metric =>(
                    <Line
                        key={metric}
                        type="monotone"
                        dataKey={metric}
                    />
                ))}
            </LineChart>

        </div>
    )
}
