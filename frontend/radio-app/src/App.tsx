import React, { useState } from "react"
import style from './App.module.scss'


type Article = {
    id: number,
    title: string,
    author: string,
    link: string,
    published_date: string,
    pdf_path: string,
    content: string
}


type BackendDataResponse = Article[]

type DateType = {
    day: string,
    month: string,
    year: string
}

const API_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8001"

const App: React.FC = () => {
    const [data, setData] = useState<BackendDataResponse | null>(null)
    const [loading, setLoading] = useState<boolean>(false)
    const [error, setError] = useState<string | null>(null)

    const [startDate, setStartDate] = useState<DateType>({ day: "10", month: "10", year: "2025" })
    const [endDate, setEndDate] = useState<DateType>({ day: "20", month: "10", year: "2025" })

    const [inputData, setInputData] = useState<string>("")
    const [openArticleId, setOpenArticleId] = useState<number | null>(null)

    const toggleArticle = (id: number) => {
        setOpenArticleId(prev => (prev === id ? null : id))
    }

    const handleDateChange = (
        type: "start" | "end",
        field: keyof DateType,
        value: string
    ) => {
        const setter = type === "start" ? setStartDate : setEndDate
        setter(prev => ({ ...prev, [field]: value }))
    }

    const fetchHello = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setData(null)

        try {
            const startStr = `${startDate.day.padStart(2, "0")}.${startDate.month.padStart(2, "0")}.${startDate.year}`
            const endStr = `${endDate.day.padStart(2, "0")}.${endDate.month.padStart(2, "0")}.${endDate.year}`

            const res = await fetch(`${API_URL}/article?word=${inputData}&start_date=${startStr}&end_date=${endStr}`)

            if (!res.ok) {
                throw new Error(`Request failed with status ${res.status}`)
            }

            const json: BackendDataResponse = await res.json()
            setData(json)
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message)
            } else {
                setError("Unknown error")
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className={style.mainContainer}>
            <header className={style.header}>
                <h1>POLSKIE RADIO <span className={style.subHeader}>Archive Explorer</span></h1>
            </header>

            <div className={style.searchSection}>
                <form className={style.searchForm} onSubmit={fetchHello}>
                    <div className={style.formGroup}>
                        <label>Search Keyword</label>
                        <input
                            className={style.keywordInput}
                            type="text"
                            value={inputData}
                            onChange={(e) => setInputData(e.target.value)}
                            placeholder="e.g. Politics, Music..."
                        />
                    </div>

                    <div className={style.formGroup}>
                        <label>Date Range (DD / MM / YYYY)</label>
                        <div className={style.dateInputsRow}>
                            <div className={style.dateGroup}>
                                <span>FROM</span>
                                <input type="text" maxLength={2} value={startDate.day} onChange={(e) => handleDateChange("start", "day", e.target.value)} placeholder="DD" />
                                <span className={style.separator}>/</span>
                                <input type="text" maxLength={2} value={startDate.month} onChange={(e) => handleDateChange("start", "month", e.target.value)} placeholder="MM" />
                                <span className={style.separator}>/</span>
                                <input type="text" maxLength={4} value={startDate.year} onChange={(e) => handleDateChange("start", "year", e.target.value)} placeholder="YYYY" />
                            </div>
                            <div className={style.dateGroup}>
                                <span>TO</span>
                                <input type="text" maxLength={2} value={endDate.day} onChange={(e) => handleDateChange("end", "day", e.target.value)} placeholder="DD" />
                                <span className={style.separator}>/</span>
                                <input type="text" maxLength={2} value={endDate.month} onChange={(e) => handleDateChange("end", "month", e.target.value)} placeholder="MM" />
                                <span className={style.separator}>/</span>
                                <input type="text" maxLength={4} value={endDate.year} onChange={(e) => handleDateChange("end", "year", e.target.value)} placeholder="YYYY" />
                            </div>
                        </div>
                    </div>

                    <button type="submit" className={style.searchBtn} disabled={loading}>
                        {loading ? "SEARCHING..." : "SEARCH ARCHIVE"}
                    </button>
                </form>
            </div>

            <div className={style.resultsSection}>
                {error && <div className={style.errorMsg}>{error}</div>}

                {data && (
                    <>
                        <div className={style.resultsHeader}>Found {data.length} articles</div>
                        <div className={style.resultsGrid}>
                            {data.map((article) => (
                                <div key={article.id} className={`${style.articleCard} ${openArticleId === article.id ? style.expanded : ''}`}>
                                    <div className={style.cardHeader}>
                                        <div className={style.dateBadge}>{article.published_date}</div>
                                        <div className={style.actions}>
                                            <a href={`${API_URL}/pdfs/${article.pdf_path}`} target="_blank" rel="noopener noreferrer" className={style.iconBtn} title="Download PDF">
                                                PDF
                                            </a>
                                            <a href={article.link} target="_blank" rel="noopener noreferrer" className={style.iconBtn} title="View Original">
                                                LINK
                                            </a>
                                        </div>
                                    </div>

                                    <h3>{article.title}</h3>
                                    <p className={style.author}>By {article.author}</p>

                                    <button className={style.expandBtn} onClick={() => toggleArticle(article.id)}>
                                        {openArticleId === article.id ? "Hide Content" : "Read Content"}
                                    </button>

                                    {openArticleId === article.id && (
                                        <div className={style.cardContent}>
                                            {article.content || "No text content available."}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}

export default App
