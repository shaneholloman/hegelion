import Hero from './components/Hero'
import QuickStart from './components/QuickStart'
import WhatHegelionDoes from './components/WhatHegelionDoes'
import UnderstandingProcess from './components/UnderstandingProcess'
import TechnicalArchitecture from './components/TechnicalArchitecture'
import PerformanceCharacteristics from './components/PerformanceCharacteristics'
import TrainingResults from './components/TrainingResults'
import Applications from './components/Applications'
import CurrentStatus from './components/CurrentStatus'
import BusinessModel from './components/BusinessModel'
import TechnicalSpecs from './components/TechnicalSpecs'
import ForResearchers from './components/ForResearchers'
import ForInvestors from './components/ForInvestors'
import Footer from './components/Footer'

function App() {
  return (
    <div className="App">
      <Hero />
      <QuickStart />
      <WhatHegelionDoes />
      <UnderstandingProcess />
      <TechnicalArchitecture />
      <PerformanceCharacteristics />
      <TrainingResults />
      <Applications />
      <CurrentStatus />
      <BusinessModel />
      <TechnicalSpecs />
      <ForResearchers />
      <ForInvestors />
      <Footer />
    </div>
  )
}

export default App

