const briefText = $input.first().json.output ?? '';
const intermediateSteps = $('Research Agent').first().json.intermediateSteps ?? [];

// Collect all URLs actually returned or fetched across tool calls
const observedUrls = new Set();

for (const step of intermediateSteps) {
  const obs = step.observation;
  if (typeof obs === 'string') {
    const urls = obs.match(/https?:\/\/[^\s"'<>\)]+/g) || [];
    urls.forEach(u => observedUrls.add(u));
  } else if (typeof obs === 'object' && obs !== null) {
    const str = JSON.stringify(obs);
    const urls = str.match(/https?:\/\/[^\s"'<>\)]+/g) || [];
    urls.forEach(u => observedUrls.add(u));
  }
}

// Extract URLs cited in the final brief
const citedUrls = briefText.match(/https?:\/\/[^\s"'<>\)]+/g) || [];
const unverifiedCitations = [];

for (const url of citedUrls) {
  const cleanUrl = url.replace(/[,\.\)]+$/, '');
  const isObserved = Array.from(observedUrls).some(ou => ou.includes(cleanUrl) || cleanUrl.includes(ou));
  if (!isObserved) {
    unverifiedCitations.push(cleanUrl);
  }
}

const isValid = unverifiedCitations.length === 0;

return [{
  json: {
    briefText,
    citedUrls: [...new Set(citedUrls)],
    observedUrls: Array.from(observedUrls),
    unverified_citations: unverifiedCitations,
    isValid,
    needs_repair: !isValid,
    toolCallCount: intermediateSteps.length
  }
}];
