import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroSection}>
      {/* Background Gradient */}
      <div className={styles.heroBackground}></div>

      {/* Background Video (Center) */}
      <video
        className={styles.heroVideo}
        autoPlay
        loop
        muted
        playsInline
        poster="/img/hero-poster.jpg"
      >
        <source src="/videos/hero-video.mp4" type="video/mp4" />
      </video>

      {/* Floating Circles Decoration */}
      <div className={styles.floatingCircles}></div>

      {/* Top-Left: Main Title */}
      <div className={styles.topLeft}>
        <h1 className={styles.mainTitle}>
          PHYSICAL AI &<br />
          HUMANOID ROBOTICS
        </h1>
      </div>

     
      <div className={styles.bottomLeft}>
        <p className={styles.subtitle}>
          CURRICULUM FOR ASPIRING<br />
          ROBOTICS ENGINEERS
        </p>
        <Link className={styles.ctaButton} to="/docs/intro">
          START LEARNING
        </Link>
        <Link className={styles.secondaryLink} to="#modules">
          EXPLORE MODULES
        </Link>
      </div>

      {/* Bottom-Center: Footer Text */}
      <div className={styles.bottomCenter}>
        <p className={styles.footerText}></p>
      </div>

    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title={`${siteConfig.title}`} description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
