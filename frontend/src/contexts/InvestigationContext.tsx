import { createContext, useContext, useState, ReactNode } from 'react'

interface InvestigationState {
  currentQuestion: string | null
  currentAnswer: string | null
  currentPipeline: string | null
  investigationId: string | null
  isComplete: boolean
  timestamp: string | null
}

interface InvestigationContextType {
  investigation: InvestigationState
  setInvestigation: (data: Partial<InvestigationState>) => void
  clearInvestigation: () => void
}

const defaultState: InvestigationState = {
  currentQuestion: null,
  currentAnswer: null,
  currentPipeline: null,
  investigationId: null,
  isComplete: false,
  timestamp: null
}

const InvestigationContext = createContext<InvestigationContextType | undefined>(undefined)

export function InvestigationProvider({ children }: { children: ReactNode }) {
  const [investigation, setInvestigationState] = useState<InvestigationState>(defaultState)

  const setInvestigation = (data: Partial<InvestigationState>) => {
    setInvestigationState(prev => ({ ...prev, ...data, timestamp: new Date().toISOString() }))
  }

  const clearInvestigation = () => {
    setInvestigationState(defaultState)
  }

  return (
    <InvestigationContext.Provider value={{ investigation, setInvestigation, clearInvestigation }}>
      {children}
    </InvestigationContext.Provider>
  )
}

export function useInvestigation() {
  const context = useContext(InvestigationContext)
  if (context === undefined) {
    throw new Error('useInvestigation must be used within an InvestigationProvider')
  }
  return context
}
