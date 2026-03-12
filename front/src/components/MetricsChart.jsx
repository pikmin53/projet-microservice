import {LineChart,Line,XAxis,YAxis,Tooltip,CartesianGrid,Legend} from "recharts"

export default function MetricsChart({data,title,unit}){
    const metricKeys = data.length > 0 ? Object.keys(data[0]).filter(key => key !== 'time') : [];

    return(
        <div style={{marginBottom:40}}>
            <h3>{title}</h3>

            <LineChart width={1000} height={300} data={data} margin={{top: 10, right: 100, left: 100, bottom: 5}}>
                <CartesianGrid strokeDasharray="3 3"/>
                <XAxis dataKey="time"/>
                <YAxis unit={unit}/>
                <Tooltip/>

                {metricKeys.map(metric =>(
                    <Line
                        key={metric}
                        type="monotone"
                        dataKey={metric}
                        name = {metric}
                        isAnimationActive={false}
                    />
                ))}
            </LineChart>

        </div>
    )
}
